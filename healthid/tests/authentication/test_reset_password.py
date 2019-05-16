import json

from django.conf import settings

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import (password_reset_json,
                                                         password_reset_query)


class TestResetPassword(BaseConfiguration):
    """
    Class to test for user ability to reset
    their password.
    """

    def setUp(self):
        super().setUp()
        self.valid_email = self.new_user["email"]
        self.invalid_email = "jillo.woche@andela.com"
        self.new_valid_password = "Password1234"
        self.new_invalid_password = "pass"
        self.valid_response = self.query(
            password_reset_query.format(email=self.valid_email))
        self.invalid_response = self.query(
            password_reset_query.format(email=self.invalid_email))

        self.reset_password = self.valid_response['data']["resetPassword"]
        self.valid_link = self.reset_password["resetLink"]
        self.invalid_link = self.valid_link + "randomstring"

        self.valid_json = password_reset_json.format(
            password=self.new_valid_password)
        self.invalid_json = password_reset_json.format(
            password=self.new_invalid_password)

    def test_link_with_valid_email(self):
        """
        Method to test if a reset link can be generated
        for an email that exists.
        """
        self.assertIn(
            "resetLink", self.valid_response['data']["resetPassword"])
        self.assertIn("check your email for a password reset link",
                      self.valid_response['data']["resetPassword"]["success"])

    def test_successful_reset(self):
        """
        Method to test if password can be reset for
        a valid email.
        """
        response = self.client.put(
            self.valid_link,
            self.valid_json,
            content_type='application/json')
        message = json.loads(response._container[0])
        self.assertIn("successfully reset", message["message"])
        self.assertEqual(response.status_code, 200)

    def test_redirect_valid_link(self):
        """
        Method to test if password can be reset for
        a valid email.
        """
        response = self.client.get(
            self.valid_link,
            content_type='application/json')
        self.assertIn(f"{settings.FRONTEND_URL}/reset_password", response.url)
        self.assertEqual(response.status_code, 302)  # test redirection

    def test_redirect_invalid_link(self):
        """
        Method to test if password can be reset for
        a valid email.
        """
        response = self.client.get(
            self.invalid_link,
            content_type='application/json')
        self.assertIn('Reset link is expired or corrupted',
                      response.context[0]['small_text_detail'])
        self.assertEqual(response.status_code, 400)  # test redirection

    def test_reset_with_invalid_password(self):
        """
        Method to test the correct response for a
        password that is not valid.
        """
        response = self.client.put(
            self.valid_link,
            self.invalid_json,
            content_type='application/json')
        message = json.loads(response._container[0])
        self.assertIn("password must have at least 8 characters",
                      message["message"])
        self.assertEqual(response.status_code, 400)

    def test_link_with_non_existing_email(self):
        """
        Method to test if a reset link can be generated
        for an email that is not yet registered.
        """
        self.assertIn("Email address not found!",
                      self.invalid_response["errors"][0]["message"])

    def test_invalid_reset_link(self):
        """
        Method to test if an invalid reset link can
        be used to reset password
        """
        response = self.client.put(
            self.invalid_link,
            self.valid_json,
            content_type='application/json'
        )
        message = json.loads(response._container[0])
        self.assertIn("Verification link is corrupted or expired",
                      message["message"])
        self.assertEqual(response.status_code, 401)

    def test_with_blank_email(self):
        """
        Method to test correct error message should
        the email field be left blank.
        """
        blank_email = " "
        response = self.query(
            password_reset_query.format(email=blank_email))

        self.assertIn("Please provide your email",
                      response["errors"][0]["message"])
