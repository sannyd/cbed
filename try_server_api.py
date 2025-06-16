import base64
from datetime import datetime, timedelta

from appstoreserverlibrary.api_client import AppStoreServerAPIClient, APIException
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.models.NotificationHistoryRequest import NotificationHistoryRequest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
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
environment = Environment.PRODUCTION

client = AppStoreServerAPIClient(private_key_raw_string, key_id, issuer_id, bundle_id, environment)

# response = client.request_test_notification()
# response = client.get_test_notification_status("fa2f0879-9adc-4ada-adcd-d38c0ab42805_1742490273151")
# # print(response)
# jwt_payload = response.signedPayload
# # read JWT
# payload = jwt_payload.split(".")[1]
# print(payload)
# json_payload = base64.b64decode(payload + "==").decode("utf-8")
# print(json_payload)
response = client.get_notification_history(None,
NotificationHistoryRequest(
startDate=int((datetime.now() - timedelta(days=10)).timestamp())*1000,
endDate=int((datetime.now()).timestamp())*1000,
)
)
print(response.notificationHistory[0].signedPayload)
# read JWT