from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.login import login_user, login_user_email


class LoginTestCase(BaseConfiguration):

    def test_login_user(self):
        response = self.query(
            login_user(
                self.new_user['mobile_number'], self.new_user['password'])
        )
        self.assertIn("Login Successful",
                      response["data"]["loginUser"]['message'])

    def test_login_email(self):
        response = self.query(
            login_user_email(
                self.new_user['email'], self.new_user['password'])
        )
        self.assertIn("Login Successful",
                      response["data"]["loginUser"]['message'])

    def test_invalid_login(self):
        response = self.query(
            login_user_email("me@you", "this"))
        self.assertIn("Invalid login credentials",
                      response["data"]["loginUser"]['message'])

    def test_invalid_number(self):
        response = self.query(
            login_user("25499999999", "this"))
        self.assertIn("Invalid login credentials",
                      response["data"]["loginUser"]['message'])
