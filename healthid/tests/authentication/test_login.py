from graphql_jwt.testcases import JSONWebTokenTestCase

from healthid.apps.authentication.models import User
from healthid.tests.authentication.test_data import (
    login_mutation,
    login_user_query,
    test_users_query
)
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class UserTests(JSONWebTokenTestCase):
    """
    Class to test for user authentication.
    """

    def setUp(self):
        self.client.execute(login_user_query)
        self.login_user = User.objects.get(email="user@gmail.com")
        self.login_user.is_active = True
        self.login_user.save()
        self.client.authenticate(self.login_user)

    def test_get_user(self):
        # Check if testuser exists in the database
        response = self.client.execute(test_users_query)
        self.assertEqual(str(self.login_user.id),
                         response.data['users'][0]["id"])

    def test_correct_user_login(self):
        # Test if the created user can be logged in
        # and a token generated.
        variables = {
            'email': self.login_user.email,
            'password': "Passsword12"
        }
        response = self.client.execute(login_mutation, variables=variables)
        self.assertEqual(str(self.login_user.id),
                         response.data['tokenAuth']['user']['id'])
        self.assertGreater(len(response.data['tokenAuth']['token']), 10)

    def test_incorrect_email_login(self):
        # Test if the user can log in with an incorrect email.
        variables = {
            'email': 'wrong_user@gmail.com',
            'password': 'Passsword12'
        }
        response = self.client.execute(login_mutation, variables=variables)
        self.assertIn(ERROR_RESPONSES[
                      "invalid_login_credentials"], str(response.errors))

    def test_incorrect_password_login(self):
        # Test if the user can log in with a wrong password.
        variables = {
            'email': 'wrong_user@gmail.com',
            'password': 'Incorrect1234'
        }
        response = self.client.execute(login_mutation, variables=variables)
        self.assertIn(ERROR_RESPONSES[
                      "invalid_login_credentials"], str(response.errors))
