import re
from functools import wraps

from graphql import GraphQLError

from .validations import ValidateUser


class UpdateUser:

    # This class contains methods to help with updating of user details

    def update_user(self, instance, **kwargs):
        for key, value in kwargs.items():
            if key == 'password':
                password = value[0].new_password

            if key is not None:
                setattr(instance, key, value)
        instance.set_password(password)
        instance.save()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mobile_number = kwargs.get('mobile_number')
            password_input = kwargs.get('password')
            new_password = password_input[0]['new_password']
            ValidateUser().validate_mobileNumber(mobile_number)
            ValidateUser().validate_password(new_password)
            return func(*args, **kwargs)
        return wrapper


instance = UpdateUser()
