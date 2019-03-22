import json

from django.db import connection
from django.test import Client, TestCase

from healthid.apps.authentication.models import Role, User

from healthid.apps.authentication.tests.test_data import query_str


class TestAdminRegistration(TestCase):

    def setUp(self):
        self._client = Client()
        self.role = Role.objects.create(name='Master Admin')
        self.user = User.objects.create_user(
            email='healthid@gmail.com',
            password='healthID',
            mobile_number=78766363,
        )
        self.user.role = self.role
        self.user.is_active = True
        self.user.save()
        self._client.login(
            email="healthid@gmail.com",
            password="healthID")

        self.user_data = {
            'firstname': 'kafuuma',
            'lastname': 'henry',
            'username': 'kafuumahenry',
            'email': 'healthid@gmail.com',
            'phone': +256788088831
        }

    def query(self, query: str):
        body = {'query': query}
        response = self._client.post(
            '/healthid/', json.dumps(body), content_type='application/json',
        )
        json_response = json.loads(response.content.decode())
        return json_response

    def test_update_admin_profile(self):
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertNotIn('errors', response)
        self.assertIn('success',
                      response['data']['updateAdminUser']
                      )

    def test_update_admin_profile_doesnot_exists(self):
        self.user.delete()
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'You do not have permission to perform this action'
        )

    def test_update_admin_profile_with_invalid_email(self):
        self.user_data['id'] = str(self.user.id)
        self.user_data['email'] = 'invalidemailadress'
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'invalidemailadress is not a valid email address'
        )

    def test_update_admin_profile_with_invalid_username(self):
        self.user_data['id'] = str(self.user.id)
        self.user_data['username'] = '#$**********'
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'names must not contain special characters'
        )

    def test_update_admin_profile_with_invalid_phone_number(self):
        self.user_data['id'] = str(self.user.id)
        self.user_data['phone'] = '00778'
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'Please input a valid mobileNumber'
        )

    def test_update_admin_profile_with_very_long_name(self):
        self.user_data['id'] = str(self.user.id)
        self.user_data['lastname'] = 'verylongne'*100
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'a name cannnot exceed 30 characters'
        )

    def test_update_admin_profile_with_empty_name_field(self):
        self.user_data['id'] = str(self.user.id)
        self.user_data['lastname'] = ''
        response = self.query(
            query_str.format(**self.user_data),
        )
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'a name field must not be empty'
        )
