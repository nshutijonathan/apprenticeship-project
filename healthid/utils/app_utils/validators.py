import re

from graphql import GraphQLError


def validate_email(email):
    email = email.strip()

    if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                email) is None:
        raise GraphQLError('Please input a valid email'.format(email))
    return email


def special_cahracter_validation(string):
    string_regex = re.search(r'[^a-zA-Z0-9.,\-\s]+', string)
    if string_regex is not None:
        raise GraphQLError("special characters not allowed")


def validate_password(new_password):
    password_regex = '(?=.{8,100})(?=.*[A-Z])(?=.*[0-9])'
    if re.match(password_regex, new_password) is None:
        error = ('password must have at least 8 characters,'
                 ' a number and a capital letter.')
        return error
