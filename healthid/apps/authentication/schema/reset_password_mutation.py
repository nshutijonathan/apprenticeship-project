from os import environ, getenv

import graphene
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from graphql import GraphQLError

from healthid.apps.authentication.models import User
from healthid.utils.auth_utils.tokens import account_activation_token

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class ResetPassword(graphene.Mutation):
    """
    Functions of this mutation class:
    1. Receive user email and check that user exists.
    2. Generate a token for resetting password.
    3. Create a reset password link using the token.
    4. Send the user a password reset email.
    """
    reset_link = graphene.Field(graphene.String)
    success = graphene.Field(graphene.String)

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        if email.strip() == "":
            raise GraphQLError(
                "Please provide your email to reset your password.")

        user = User.objects.filter(email=email).first()
        if user is None:
            raise GraphQLError("Email address not found! "
                               "Please use the email you registered with.")

        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(
            user.pk)).decode()
        user_firstname = user.first_name
        if not user_firstname:
            user_firstname = "User"

        # Send email to the user
        html_body = render_to_string(
            'emails/password_reset_email.html', {
                'name': user_firstname,
                'email': email,
                'domain': DOMAIN,
                'uid': uid,
                'token': token,
            })

        msg = EmailMessage(
            subject='Password Reset',
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email])
        msg.content_subtype = 'html'
        msg.send()

        reset_link = "{}/healthid/password_reset/{}/{}".format(
            DOMAIN, uid, token)
        success = "Please check your email for a password reset link."
        success += " Look inside your Spam folder in case you cannot trace it."

        return ResetPassword(reset_link=reset_link, success=success)
