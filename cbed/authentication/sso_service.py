import facebook
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed

from config.exception import FacebookNotLinkedToEmailException


class SSOService:
    @staticmethod
    def verify_google_auth(access_token):
        # try:
            id_info = id_token.verify_token(access_token, requests.Request())
            return id_info["email"]
        # except ValueError:
        #     raise AuthenticationFailed

    @staticmethod
    def verify_facebook_auth(access_token):
        try:
            graph = facebook.GraphAPI(access_token=access_token)
            user_info = graph.request(path="me?fields=email")
        except Exception:
            raise AuthenticationFailed

        if "email" not in user_info:
            raise FacebookNotLinkedToEmailException()

        return user_info["email"]
