from django.test import TestCase
from graphene.test import Client
import json

from healthid.schema import schema
from healthid.apps.authentication.models import User
from .test_data import userquery


class UserTests(TestCase):
    """
    Class to test for logged in users
    """
    def setUp(self):
        self.client = Client(schema)
        self.user = User(
            mobile_number=729041783,
            password="123456",
            email="testuser@gmail.com"
        )

        self.user.is_active = True
        self.user.save()

        self.client.execute(userquery)

        self.login_user = User.objects.get(email="user@gmail.com")
        self.login_user.is_active = True
        self.login_user.save()

    def test_get_user(self):
        """
        Test if testuser exists in the database
        """
        query = '''
            query GetUsers {
                users {
                    id
                }
            }
            '''

        response = self.client.execute(query)
        self.assertEqual(str(self.user.id), response['data']['users'][0]['id'])

    def test_user_login(self):
        """
        Test if the created user can be logged in
        and a token generated.
        """

        mutation = '''
            mutation GetToken($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password) {
                token
                }
            }
            '''
        variables = {
            'email': 'user@gmail.com',
            'password': 'user'
        }

        response = self.client.execute(mutation, variables=variables)
        self.assertEqual(str(self.user.id), response['data']['users'][0]['id'])
