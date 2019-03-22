from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from healthid.apps.authentication.models import User
from healthid.apps.authentication.utils.tokens import account_activation_token
from healthid.apps.authentication.views import activate


class VerificationTestCase(TestCase):
    def verify_account(self, uidb64, token):
        self._client = Client()
        request = Client().get(
            reverse("activate", kwargs={
                "token": token,
                "uidb64": uidb64
            }))

        response = activate(request, uidb64, token)
        return response

    def test_account_verified(self):
        user = User.objects.create_user(
            password='Password12',
            email='healthid@gmail.com',
            mobileNumber=+256788088831)
        token = account_activation_token.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        response = self.verify_account(token, uidb64)
        self.assertTrue(200, response.status_code)
