"""
GeoIP utilities for the cbed backend — stdlib only.

Captures the true client IP and best-effort city/region/country on every
quiz submission. NEVER blocks quiz saves on lookup failure.

Cloudflare passes two headers on every request through the WAF:
  HTTP_CF_CONNECTING_IP  — the true client IP (replaces REMOTE_ADDR)
  HTTP_CF_IPCOUNTRY       — 2-letter ISO country code (free, no library)

For city/region we hit ip-api.com's free HTTP endpoint (no API key,
45 req/min, response cached in Django's default cache for 7 days).
The lookup runs with a 1.5s timeout and is wrapped in try/except — slow
or unreachable ip-api.com cannot slow quiz saves.

Uses urllib.request from stdlib so we never have to add a dependency
(this lesson was learned the hard way: adding requests==2.32.3 to
requirements/base.txt caused pip wheel to drop setuptools, which broke
drf_yasg → container crash loop → API outage).
"""
import json
import logging
import socket
import ipaddress
import urllib.request
import urllib.error
import urllib.parse

from django.core.cache import cache

logger = logging.getLogger(__name__)


# --- IP extraction ---

def _get_client_ip(request):
    """Return the true client IP.

    Priority:
      1. HTTP_CF_CONNECTING_IP  — Cloudflare (always present, true client IP)
      2. HTTP_X_FORWARDED_FOR   — first hop in standard proxy chain
      3. REMOTE_ADDR            — direct TCP peer (nginx/gunicorn)

    Always returns a string or '' — never raises.
    """
    cf = request.META.get('HTTP_CF_CONNECTING_IP', '').strip()
    if cf:
        return cf
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '').strip()
    if xff:
        first = xff.split(',')[0].strip()
        if first:
            return first
    remote = request.META.get('REMOTE_ADDR', '').strip()
    return remote or ''


def _get_country_from_cloudflare(request):
    """Return the 2-letter ISO country code Cloudflare knows, or ''.

    Free header, always present in production (CF passes it on every
    request). 'XX' means Cloudflare couldn't determine the country.
    """
    country = (request.META.get('HTTP_CF_IPCOUNTRY', '') or '').strip().upper()
    if country and country != 'XX' and len(country) == 2:
        return country
    return ''


def _is_private_ip(ip):
    """True for loopback, link-local, RFC 1918, ULA, CGNAT, etc.

    We skip lookups for these — they're either our own infra (nginx,
    Cloudflare workers) or impossible to geolocate accurately.
    """
    if not ip:
        return True
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return True
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_unspecified
        or addr.is_reserved
    )


# --- Cache helpers ---

CACHE_KEY_PREFIX = 'geoip:v1:'
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days
NEG_CACHE_TTL_SECONDS = 300       # 5 min for failed lookups


def _lookup_geolocation(ip, timeout=1.5):
    """Hit ip-api.com free endpoint for city/region/country. Cached 7 days.

    Returns dict {city, region, country, country_name, ip} on success,
    None on any failure. The lookup is strictly bounded by `timeout`
    seconds so a slow upstream can never hang a quiz save.
    """
    if not ip or _is_private_ip(ip):
        return None

    cache_key = f'{CACHE_KEY_PREFIX}{ip}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached if cached else None  # late in format string, intentional

    # ip-api.com free tier: http://ip-api.com/json/{ip}
    # fields param limits which keys come back (saves bandwidth).
    url = f'http://ip-api.com/json/{urllib.parse.quote(ip)}'
    fields = 'status,city,regionName,country,countryCode,query'
    full_url = f'{url}?fields={fields}'

    try:
        req = urllib.request.Request(
            full_url,
            headers={'User-Agent': 'cbed-backend/1.0'},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            data = json.loads(body.decode('utf-8', errors='replace'))
            if data.get('status') == 'success':
                out = {
                    'city': (data.get('city') or '').strip(),
                    'region': (data.get('regionName') or '').strip(),
                    'country': (data.get('countryCode') or '').strip(),
                    'country_name': (data.get('country') or '').strip(),
                    'ip': ip,
                }
                cache.set(cache_key, out, CACHE_TTL_SECONDS)
                return out
            # Negative cache: status != success at either rate-limit or junk IP
            cache.set(cache_key, False, NEG_CACHE_TTL_SECONDS)
            return None
    except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout,
            TimeoutError, ConnectionError, OSError, json.JSONDecodeError, ValueError) as e:
        # ANY failure → silent skip. Quiz save must never depend on geo.
        logger.warning('geoip lookup failed for %s: %s', ip, e)
        cache.set(cache_key, False, NEG_CACHE_TTL_SECONDS)
        return None


# --- Public entry point ---

def capture_request_geo(request, ip=None):
    """Capture client IP + best-effort geolocation for the given request.

    Returns dict:
      ip                str  — client IP ('' if unknown)
      country           str  — 2-letter country code (from CF if available,
                                else from ip-api.com lookup, else '')
      city              str  — city (from ip-api.com or '')
      region            str  — region/state (from ip-api.com or '')
      country_name      str  — full country name (from ip-api.com or '')
      geo_source        str  — 'cloudflare+ip-api' | 'cloudflare_only' |
                                'ip-api_only' | 'unavailable'

    Safe to use inside any view — never raises, never blocks for more than
    the lookup timeout (1.5s).
    """
    if ip is None:
        ip = _get_client_ip(request)
    country_cf = _get_country_from_cloudflare(request)

    if not ip or _is_private_ip(ip):
        # No usable IP for an external lookup; rely on CF country if present.
        return {
            'ip': ip or '',
            'country': country_cf,
            'city': '',
            'region': '',
            'country_name': '',
            'geo_source': 'cloudflare_only' if country_cf else 'unavailable',
        }

    full = _lookup_geolocation(ip)
    if full:
        return {
            'ip': ip,
            'country': full.get('country') or country_cf,
            'city': full.get('city') or '',
            'region': full.get('region') or '',
            'country_name': full.get('country_name') or '',
            'geo_source': 'cloudflare+ip-api' if country_cf else 'ip-api_only',
        }

    # ip-api.com unreachable; CF country may still be useful.
    return {
        'ip': ip,
        'country': country_cf,
        'city': '',
        'region': '',
        'country_name': '',
        'geo_source': 'cloudflare_only' if country_cf else 'unavailable',
    }