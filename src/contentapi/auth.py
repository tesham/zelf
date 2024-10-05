from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from rest_framework import exceptions

class SafeAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth_key = request.headers.get('x-api-key')

        if auth_key!=settings.JWT_SECRET_KEY:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (True,None)
