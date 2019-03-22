
import re

from graphql import GraphQLError
from graphql_jwt.decorators import login_required


class ValidateAdmin:
    """This class validates user admin fields
    """

    def validate_admin_fields(self, **kwargs):
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', '')
        username = kwargs.get('username', '')
        secondary_email = kwargs.get('secondary_email', '')
        secondary_phone_number = kwargs.get(
            'secondary_phone_number', '')
        return{
            "first_name": self._validate_name(first_name),
            "last_name": self._validate_name(last_name),
            "username": self._validate_name(username),
            "secondary_email": self._validate_secondary_email(secondary_email),
            "secondary_phone_number":
            self._validate_secondary_phone_number(secondary_phone_number)
        }

    def _validate_name(self, name):

        name = name.strip()
        if not len(name) > 0:
            raise GraphQLError('a name field must not be empty')

        if not len(name) < 30:
            raise GraphQLError('a name cannnot exceed 30 characters')
        if re.match('^[A-Za-z0-9_]*$', name) is None:
            raise GraphQLError('names must not contain special characters')

        return name

    def _validate_secondary_email(self, email):

        email = email.strip()
        if re.match('^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                    email) is None:
            raise GraphQLError(f'{email} is not a valid email address')
        return email

    def _validate_secondary_phone_number(self, phone_number):

        phone_number = phone_number.strip()
        if re.match(
            '^\+?\(?\d{3}\)?[-. ]?\d{9}$',
                phone_number) is None:
            raise GraphQLError('Please input a valid mobileNumber')
        return phone_number


validate_instance = ValidateAdmin()
