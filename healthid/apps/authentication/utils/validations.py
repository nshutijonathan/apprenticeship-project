import re

from graphql import GraphQLError


class ValidateUser:
    def validate_user_fields(self, email, password, mobile_number):
        return {
            "email": self.validate_email(email),
            "mobile_number": self.validate_mobileNumber(mobile_number),
            "password": self.validate_password(password),
        }

    def validate_email(self, email):
        email = email.strip()
        if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                    email) is None:
            raise GraphQLError('Please input a valid email'.format(email))
        return email

    def validate_mobileNumber(self, mobile_number):
        mobile_number = mobile_number.strip()
        if re.match(r'^\+?\(?\d{3}\)?[-. ]?\d{9}$', mobile_number) is None:
            raise GraphQLError('Please input a valid mobile number')
        return mobile_number

    def validate_password(self, password):
        password = password.strip()
        if not len(password) > 0:
            raise GraphQLError(
                'passwords must be bettween 8 to 100 characters')
        if not len(password) < 100:
            raise GraphQLError(
                'passwords must be bettween 8 to 100 characters')
        msg = 'password must contain atleast one number and a capital letter.'
        if (re.search('[0-9]', password) is None):
            raise GraphQLError(msg)
        if (re.search('[A-Z]', password) is None):
            raise GraphQLError(msg)
        return password
