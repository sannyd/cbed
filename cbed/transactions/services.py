import base64
import json
from datetime import datetime, timedelta

from appstoreserverlibrary.api_client import AppStoreServerAPIClient
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.models.NotificationHistoryRequest import NotificationHistoryRequest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cbed.transactions.models import AppStoreRawTransaction, Transaction

private_key_raw_string = b"""-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg7EjcmwITAhcZIY+A
aeYdBol2Ergz+oWHUUUvO1vl/FOgCgYIKoZIzj0DAQehRANCAAS7WvsZY4v+zixk
Dhcj4+PzPNHG5LIki+78s1du0yLHhkDhsO8sweaEiNhX8dTEHauy+mP7wl3xijVc
g5YlFhBv
-----END PRIVATE KEY-----"""
private_key = serialization.load_pem_private_key(
    private_key_raw_string,
    password=None,  # Use bytes if the key is encrypted, e.g., b"your_password"
    backend=default_backend()
)

key_id = "LK7CMR6RDF"
issuer_id = "69a6de88-9acd-47e3-e053-5b8c7c11a4d1"
bundle_id = "com.barexamdrills.app"


class TransactionService:
    @staticmethod
    def sync_app_store_transactions():
        environment = Environment.PRODUCTION
        client = AppStoreServerAPIClient(private_key_raw_string, key_id, issuer_id, bundle_id, environment)
        response = client.get_notification_history(None,
                                                   NotificationHistoryRequest(
                                                       startDate=int(
                                                           (datetime.now() - timedelta(days=1)).timestamp()) * 1000,
                                                       endDate=int((datetime.now()).timestamp()) * 1000,
                                                   )
                                                   )
        count = 0
        for history in response.notificationHistory:
            payload = history.signedPayload.split(".")[1]
            json_payload_str = base64.b64decode(payload + "==").decode("utf-8")
            json_payload = json.loads(json_payload_str)
            """{"notificationType":"TEST","notificationUUID":"fa2f0879-9adc-4ada-adcd-d38c0ab42805","data":{"appAppleId":1466447387,"bundleId":"com.barexamdrills.app","environment":"Production"},"version":"2.0","signedDate":1742490273153}"""
            if AppStoreRawTransaction.objects.filter(uuid=json_payload["notificationUUID"]).first():
                continue
            AppStoreRawTransaction.objects.create(
                uuid=json_payload["notificationUUID"],
                json=json_payload,
                raw=history.signedPayload
            )
            count += 1

        return f"Synced {count} transactions"

    @classmethod
    def check_refund_state(cls):
        count = 0
        for raw_transaction in AppStoreRawTransaction.objects.filter(
                json__contains={"notificationType": "REFUND"}
        ):
            tx_info_b64 = raw_transaction.json['data']['signedTransactionInfo'].split(".")[1]
            tx_info = base64.b64decode(tx_info_b64 + "==").decode("utf-8")
            tx_info_json = json.loads(tx_info)
            originalTransactionId= tx_info_json['originalTransactionId']
            transaction = Transaction.objects.filter(ref=originalTransactionId).first()
            if transaction:
                transaction.is_refunded = True
                transaction.save()
                count += 1

        return f"Checked {count} refunds"