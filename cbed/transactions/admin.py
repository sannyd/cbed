from django.contrib import admin
from django.contrib.admin import ModelAdmin

from cbed.transactions.models import Transaction, AppStoreRawTransaction


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ["user", "product", "ref", "created"]
    list_filter = [
        "product",
    ]

@admin.register(AppStoreRawTransaction)
class AppStoreRawTransactionAdmin(ModelAdmin):
    list_display = ["uuid", "created"]
    search_fields = ["uuid"]