from django.contrib.auth import authenticate

import graphene
from graphql_jwt.utils import jwt_encode, jwt_payload
from django.core.exceptions import ObjectDoesNotExist
from healthid.apps.authentication.models import User
from healthid.apps.authentication.schema.auth_queries import UserType


class LoginUser(graphene.Mutation):
    message = graphene.String()
    token = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        mobile_number = graphene.String()
        password = graphene.String()
        email = graphene.String()

    def mutate(self, info, **kwargs):
        email = kwargs.get('email')
        mobile_number = kwargs.get('mobile_number')
        password = kwargs.get('password')
        if email is None:
            try:
                user = User.objects.get(mobile_number=mobile_number)
                email = user.email
            except ObjectDoesNotExist:
                message = "Invalid login credentials"
                return LoginUser(message=message)
        user_auth = authenticate(username=email, password=password)
        if user_auth is not None:
            message = "Login Successful"
            payload = jwt_payload(user_auth)
            token = jwt_encode(payload)
        else:
            message = "Invalid login credentials"
            token = 'none'
        return LoginUser(
            message=message,
            token=token,
            user=user_auth
        )
