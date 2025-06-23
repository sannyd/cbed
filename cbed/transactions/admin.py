import base64
import json

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html

from cbed.transactions.models import Transaction, AppStoreRawTransaction


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ["user", "is_refunded","product", "ref", "created"]
    list_filter = [
        "product", "is_refunded", "created"
    ]



@admin.register(AppStoreRawTransaction)
class AppStoreRawTransactionAdmin(ModelAdmin):
    list_display = ["uuid", "created", "raw_base64_decoded"]
    search_fields = ["uuid"]
    readonly_fields = ["raw_base64_decoded"]

    def raw_base64_decoded(self, obj):
        if 'signedTransactionInfo' in obj.json['data']:
            tx_info_b64 = obj.json['data']['signedTransactionInfo'].split(".")[1]
            tx_info = base64.b64decode(tx_info_b64 + "==").decode("utf-8")
            tx_info_json = json.loads(tx_info)
            return format_html("<pre>{}</pre>", json.dumps(tx_info_json, indent=2))
        return format_html("<pre>No signedTransactionInfo found</pre>")
    raw_base64_decoded.short_description = "Raw Base64 Decoded"