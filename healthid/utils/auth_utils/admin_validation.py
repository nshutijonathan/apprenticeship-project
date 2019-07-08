
import re

from graphql import GraphQLError
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.authentication_responses import\
      AUTH_ERROR_RESPONSES


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
            raise GraphQLError(ERROR_RESPONSES[
                               "empty_field_error"].format("name field"))

        if not len(name) < 30:
            raise GraphQLError(AUTH_ERROR_RESPONSES[
                               "characters_exceed_error"].format("a name"))
        if re.match(r'^[A-Za-z0-9_]*$', name) is None:
            raise GraphQLError(AUTH_ERROR_RESPONSES[
                               "special_characters_error"].format("names"))
        return name

    def _validate_secondary_email(self, email):

        email = email.strip()
        if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                    email) is None:
            raise GraphQLError(AUTH_ERROR_RESPONSES[
                              "invalid_email_address"].format(email))
        return email

    def _validate_secondary_phone_number(self, phone_number):

        phone_number = phone_number.strip()
        if re.match(
            r'^\+?\(?\d{3}\)?[-. ]?\d{9}$',
                phone_number) is None:
            raise GraphQLError(ERROR_RESPONSES[
                              "invalid_field_error"].format("mobileNumber"))
        return phone_number


validate_instance = ValidateAdmin()
