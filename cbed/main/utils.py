"""
GeoIP utilities for capturing client IP + location on quiz submissions.

Cloudflare passes the true client IP in `CF-Connecting-IP` and a country code
in `CF-IPCountry` (always free). City/region requires an additional lookup;
we use ip-api.com's free HTTP endpoint (no API key, 45 req/min/IP) with
Django's cache framework to keep latency low.
"""
import logging

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days — IP→location mappings are stable
CACHE_KEY_PREFIX = 'geoip:v1:'

# Test/loopback addresses we should never look up
PRIVATE_RANGES = ('127.', '10.', '192.168.', '172.16.', '172.17.', '172.18.',
                  '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
                  '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
                  '172.29.', '172.30.', '172.31.', '::1', 'fc00:', 'fe80:')


def get_client_ip(request):
    """Extract real client IP from request, handling Cloudflare + reverse proxies.

    Priority:
    1. CF-Connecting-IP (Cloudflare always sets it on proxied requests)
    2. X-Forwarded-For first hop (other reverse proxies)
    3. REMOTE_ADDR (direct connection)

    Returns IP string or None if request is unavailable.
    """
    if request is None:
        return None
    cf = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf and cf.strip():
        return cf.strip()
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        first = xff.split(',')[0].strip()
        if first:
            return first
    return request.META.get('REMOTE_ADDR')


def is_private_ip(ip):
    """Return True if IP is loopback/private — skip GeoIP lookup for these."""
    if not ip:
        return True
    return any(ip.startswith(p) for p in PRIVATE_RANGES)


def get_country_from_cloudflare(request):
    """Read CF-IPCountry header set by Cloudflare (always present, free).
    Returns 2-letter ISO country code or None.
    """
    if request is None:
        return None
    country = request.META.get('HTTP_CF_IPCOUNTRY', '').strip().upper()
    if country and country != 'XX' and len(country) == 2:
        return country
    return None


def lookup_geoip(ip, timeout=3):
    """Look up city/region/country for an IP via ip-api.com (free, 45 req/min).
    Caches in Django cache for 7 days.

    Returns dict {city, region, country, ip} on success, None on failure.
    """
    if not ip or is_private_ip(ip):
        return None

    cache_key = f"{CACHE_KEY_PREFIX}{ip}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached if cached else None

    try:
        resp = requests.get(
            f'http://ip-api.com/json/{ip}',
            params={'fields': 'status,city,regionName,country,countryCode,query'},
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                out = {
                    'city': data.get('city') or '',
                    'region': data.get('regionName') or '',
                    'country': data.get('countryCode') or '',
                    'country_name': data.get('country') or '',
                    'ip': ip,
                }
                cache.set(cache_key, out, CACHE_TTL_SECONDS)
                return out
        # Negative cache: 5 minutes (avoid hammering rate-limited endpoint)
        cache.set(cache_key, False, 300)
    except Exception as e:
        logger.warning(f'geoip lookup failed for {ip}: {e}')

    return None


def capture_request_geo(request, ip=None):
    """High-level helper used by views: extract IP, capture CF country,
    optionally do a full GeoIP lookup.

    Returns dict:
        {ip, country (from CF, free), city, region (from ip-api, cached),
         geo_source: 'cloudflare+ip-api' | 'cloudflare_only' | 'unavailable'}
    """
    if ip is None:
        ip = get_client_ip(request)
    country_cf = get_country_from_cloudflare(request)

    if not ip or is_private_ip(ip):
        return {
            'ip': ip,
            'country': country_cf,
            'city': '',
            'region': '',
            'country_name': '',
            'geo_source': 'cloudflare_only' if country_cf else 'unavailable',
        }

    # Try full lookup (cached). Use country_cf as fallback if lookup fails.
    full = lookup_geoip(ip)
    if full:
        return {
            'ip': ip,
            'country': full.get('country') or country_cf,
            'city': full.get('city') or '',
            'region': full.get('region') or '',
            'country_name': full.get('country_name') or '',
            'geo_source': 'cloudflare+ip-api',
        }

    return {
        'ip': ip,
        'country': country_cf,
        'city': '',
        'region': '',
        'country_name': '',
        'geo_source': 'cloudflare_only' if country_cf else 'unavailable',
    }