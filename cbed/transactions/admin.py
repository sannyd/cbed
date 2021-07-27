from django.contrib import admin
from django.contrib.admin import ModelAdmin

from cbed.transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ["user", "product", "ref", "created"]
    list_filter = ["product", ]
