
from os import environ, getenv

import graphene
import graphql_jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from dotenv import load_dotenv
from graphene_django import DjangoObjectType

from healthid.apps.authentication.utils.tokens import account_activation_token

from .models import User
from .utils.validations import ValidateUser

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class UserType(DjangoObjectType):
    class Meta:
        model = User

class RegisterUser(graphene.Mutation):
    """
        Mutation to register a user.
    """
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        mobile_number = graphene.String(required=True)

    success = graphene.List(graphene.String)
    errors = graphene.List(graphene.String)

    def mutate(self, info, email, password, mobile_number):
        validate_fields = ValidateUser().validate_user_fields(email, password, mobile_number)
        try:
            user = User.objects.create_user(**validate_fields)

            user.set_password(password)
            # account verification
            token = account_activation_token.make_token(user)
            html_body = render_to_string(
                'emails/verification_email.html', {
                    'name': email,
                    'domain': DOMAIN,
                    'uid': urlsafe_base64_encode(force_bytes(
                        user.pk)).decode(),
                    'token': token,
                })
            msg = EmailMessage(
                subject='Account Verification',
                body=html_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email])
            msg.content_subtype = 'html'
            msg.send()

            success = [
                "message",
                "You have succesfully registered with healthID. Please check your email to verify your account"
            ]
            return RegisterUser(success=success, user=user)
        except Exception as e:
            errors = ["Something went wrong: {}".format(e)]
            return RegisterUser(errors=errors)
        return RegisterUser(errors=errors)

class Query(graphene.AbstractType):
    """
    Query to authenticate a user.
    """
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_users(self, info):
        """
        Resolver method for users field.
        """
        return User.objects.all()

    def resolve_me(self, info):
        """
        Resolver method to check if a user is authenticated.
        """
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Please login to continue.")
        return user

class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    """
    Class to override default JSONWebTokenMutation to
    return the user object along with the authentication token.
    """
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

class Mutation(graphene.ObjectType):
    create_user = RegisterUser.Field()
