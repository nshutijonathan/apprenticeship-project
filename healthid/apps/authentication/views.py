from django.contrib import messages
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode

from healthid.apps.authentication.utils.tokens import account_activation_token

from .models import User


def activate(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64)).decode('utf-8')
        user = User.objects.get(pk=uid)

    except Exception as e:
        errors = ('Something went wrong: {}'.format(e))
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,
                         ('Your new email was successfully confirmed!'))
        return HttpResponse(
            'Thank you for your email confirmation. Now you can login into your account.'
        )
        errors = ('Something went wrong: {}'.format(e))
    return HttpResponse(errors)
