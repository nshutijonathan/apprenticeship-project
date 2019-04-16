import re

from graphql import GraphQLError
from healthid.utils.app_utils.validators import validate_email


class ValidateUser:
    def validate_user_fields(self, email, password, mobile_number):
        return {
            "email": self.validate_email(email),
            "mobile_number": self.validate_mobile_number(mobile_number),
            "password": self.validate_password(password)
        }

    def validate_email(self, email):
        return validate_email(email)

    def validate_mobile_number(self, mobile_number):
        mobile_number = mobile_number.strip()
        if re.match(r'^\+?\(?\d{3}\)?[-. ]?\d{9}$', mobile_number) is None:
            raise GraphQLError('Please input a valid mobile number')
        return mobile_number

    def validate_password(self, password):
        password = password.strip()
        if re.match('(?=.{8,100})(?=.*[A-Z])(?=.*[0-9])', password) is None:
            raise GraphQLError(
                'password must have at least 8 characters, '
                'a number and a capital letter.')
        return password

    def validate_username(self, username):
        username = username.strip()
        if re.match('(?=.*^[A-Za-z0-9_]*$)(?=.{1,30})', username) is None:
            raise GraphQLError(
                'valid username cannot be blank, contain special characters  '
                'or exceed 30 characters.')
        return username
