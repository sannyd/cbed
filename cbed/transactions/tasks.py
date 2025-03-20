from cbed.transactions.services import TransactionService
from config import celery_app


@celery_app.task()
def get_app_store_transactions():
    return TransactionService.sync_app_store_transactions()
