import re

from graphql import GraphQLError


def validate_email(email):
    email = email.strip()

    if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                email) is None:
        raise GraphQLError('Please input a valid email'.format(email))
    return email
