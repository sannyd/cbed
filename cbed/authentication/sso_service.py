import facebook
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed

from config.exception import FacebookNotLinkedToEmailException


class SSOService:
    @staticmethod
    def verify_google_auth(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request())
            return id_info["email"], id_info["picture"]
        except ValueError:
            raise AuthenticationFailed

    @staticmethod
    def verify_facebook_auth(access_token):
        try:
            graph = facebook.GraphAPI(access_token=access_token)
            user_info = graph.request(path="me?fields=id,email")
            return (
                user_info["email"],
                f'https://graph.facebook.com/{user_info["id"]}/picture?width=120',
            )
        except Exception:
            raise AuthenticationFailed
