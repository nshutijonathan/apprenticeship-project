from django.conf import settings
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import (
    register_user_query, user)


FRONTEND_URL = settings.FRONTEND_URL
HTTP = settings.HTTP


class VerificationTestCase(BaseConfiguration):

    def addUser(self):
        response = self.query(
            register_user_query.format(**user)
        )
        return response

    def test_account_verified(self):
        response = self.addUser()
        verification_link = response['data']['createUser']['verificationLink']
        response = self.client.get(
            verification_link,
            content_type='application/json')
        self.assertIn(f'{settings.FRONTEND_URL}/login', response.url)
        self.assertEqual(302, response.status_code)

    def test_account_already_verified_user(self):
        response = self.addUser()
        verification_link = response['data']['createUser']['verificationLink']
        self.client.get(verification_link, content_type='application/json')
        response = self.client.get(
            verification_link,
            content_type='application/json')
        self.assertIn(
            ('Your account is already verified,'
             ' Please click the button below to login'),
            response.context[0]['small_text_detail'])
        self.assertEqual(409, response.status_code)

    def test_expired_token(self):
        response = self.addUser()
        verification_link = response['data']['createUser']['verificationLink']
        response = self.client.get(
            verification_link+'23',
            content_type='application/json')
        self.assertIn(('We could not verify your account, the verification'
                       ' link might have expired please contact your admin'),
                      response.context[0]['small_text_detail'])
        self.assertEqual(401, response.status_code)

    def test_corrupted_token(self):
        self.addUser()
        ubd6 = 'MjQ5OHlva3V3'
        token = '56c-b773cdcdd485651e945e'
        response = self.client.get(
            f'http://{settings.FRONTEND_URL}/healthid/activate/{ubd6}/{token}',
            content_type='application/json')
        self.assertIn('This verification link is corrupted',
                      response.context[0]['small_text_detail'])
        self.assertEqual(401, response.status_code)
