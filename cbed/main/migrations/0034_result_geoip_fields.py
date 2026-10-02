"""Auto-generated: add GeoIP capture fields to main_result.

Added 2026-10-01 to enable native IP/location capture on quiz submissions,
bypassing GA4's city-throttling limitations. All fields are optional —
never block a quiz save.

Uses cbed.main.utils.capture_request_geo (stdlib-only urllib.request,
no new dependency).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0033_subscriptionplan"),
    ]

    operations = [
        migrations.AddField(
            model_name="result",
            name="client_ip",
            field=models.GenericIPAddressField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="result",
            name="geo_city",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="result",
            name="geo_region",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="result",
            name="geo_country",
            field=models.CharField(blank=True, default="", max_length=2),
        ),
        migrations.AddField(
            model_name="result",
            name="geo_country_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="result",
            name="geo_source",
            field=models.CharField(
                blank=True,
                default="",
                help_text="cloudflare+ip-api, cloudflare_only, ip-api_only, or unavailable",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="geo_captured_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
