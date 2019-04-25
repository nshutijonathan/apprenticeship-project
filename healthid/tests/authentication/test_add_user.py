from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import \
    add_user_query, admin_update_user_query


class TestAddUser(BaseConfiguration):
    """
    Testing Adding user by the Master Admin
    """

    def test_add_user(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256 754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['addUser']['errors'], None)
        self.assertEqual(resp['data']['addUser']
                         ['user']['email'], email)
        self.assertEqual(resp['data']['addUser']
                         ['user']['mobileNumber'], mobile_number)

    def test_update_user(self):
        email = 'newemail@test.com'
        firstname = 'newfirstname'
        job_title = 'Supervisor'
        mobile_number = '+256 754434483'
        user_id = self.user.id
        user_data = {
            'firstname': firstname,
            'jobTitle': job_title,
            'mobileNumber': mobile_number,
            'email': email,
            'id': user_id
        }
        resp = self.query_with_token(
            self.access_token_master,
            admin_update_user_query.format(**user_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['adminUpdateUser']['errors'], None)
        self.assertEqual(resp['data']['adminUpdateUser']
                         ['user']['email'], email)
        self.assertEqual(resp['data']['adminUpdateUser']
                         ['user']['mobileNumber'], mobile_number)
        self.assertEqual(resp['data']['adminUpdateUser']
                         ['user']['jobTitle'], job_title)

    def test_wrong_email(self):
        """
        test wrong email
        """
        email = 'test@gmail'
        mobile_number = '+256 754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id
        }

        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn("Please input a valid email",
                      resp['errors'][0]['message'])

    def test_wrong_mobile_number(self):
        """
        test wrong mobile_number
        """
        email = 'test@gmail.com'
        mobile_number = '+256 754434487aer'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id

        }

        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn("Please input a valid mobile number",
                      resp['errors'][0]['message'])

    def test_existing_email(self):
        # test if the email already exists
        email = 'john.doe@gmail.com'
        mobile_number = '+256 754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertEqual(resp['data']['addUser']
                         ['errors'], ['Something went wrong: User with email '
                                      'john.doe@gmail.com already exists'])

    def test_empty_outlet_id(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256 754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': '',
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('errors', resp)
        self.assertIn("Outlet Id cannot be Empty",
                      resp['errors'][0]['message'])

    def test_invalid_outlet_id(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256 754434487'
        outlet_id = '12121212'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': outlet_id,
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('errors', resp)
        self.assertIn(f"Outlet with id {outlet_id} does not exist.",
                      resp['errors'][0]['message'])

    def test_invalid_role_id(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256 754434487'
        role_id = '12121212'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': role_id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('errors', resp)
        self.assertIn(f"Role with id {role_id} does not exist.",
                      resp['errors'][0]['message'])
