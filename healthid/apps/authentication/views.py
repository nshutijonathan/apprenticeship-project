import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.views import View

from healthid.apps.authentication.models import User
from healthid.utils.app_utils.validators import validate_password
from healthid.utils.auth_utils.tokens import account_activation_token

FRONTEND_URL = settings.FRONTEND_URL
HTTP = settings.HTTP


def activate(request, uidb64, token):
    link = None
    check_token, user = decode_token(uidb64, token)
    if check_token and user:
        user.is_active = True
        user.save()
        return redirect(f'{HTTP}://{FRONTEND_URL}/login')

    if not check_token and user:
        if user.is_active:
            message = ('Your account is already verified,'
                       ' Please click the button below to login')
            link = f'{HTTP}://{FRONTEND_URL}/login'
            status = 409  # conflict
        else:  # token may be expired
            message = ('We could not verify your account,'
                       ' the verification link might have expired'
                       ' please contact your admin')
            status = 401  # unauthorised
    if not user and not check_token:  # token tampered with/corrupted
        message = 'This verification link is corrupted'  # link tampered with
        status = 401
    context = {
        'template_type': 'Email Verification Failed',
        'small_text_detail': message,
        'link': link
    }
    return render(
        request, 'email_alerts/verification_fail.html',
        context=context, status=status)


class PasswordResetView(View):

    def get(self, request, uidb64, token):
        check_token, user = decode_token(uidb64, token)
        if check_token and user:
            return redirect(
                f'{HTTP}://{FRONTEND_URL}/reset_password/{uidb64}/{token}'
            )
        else:
            error = ('Reset link is expired or corrupted.'
                     ' Please request another.')
            context = {
                'template_type': 'Reseting password  failed',
                'small_text_detail': error,
                'link': f'{HTTP}://{FRONTEND_URL}/login'
            }
            return render(
                request, 'email_alerts/reset_password_fail.html',
                context=context, status=400)

    def put(self, request, uidb64, token):

        data = json.loads(request.body)
        check_token, user = decode_token(uidb64, token)
        if check_token and user:
            new_password = data.get('user').get('password')
            error = validate_password(new_password)
            if error:
                message = error
                status = 400
            else:
                user.set_password(new_password)
                user.save()
                message = "Your password was successfully reset."
                status = 200
            response = {"message": message}
            return JsonResponse(response, status=status)
        else:
            message = 'Verification link is corrupted or expired'
            response = {"message": message}
        return JsonResponse(response, status=401)


def decode_token(uidb64, token):
    uid = force_bytes(urlsafe_base64_decode(uidb64)).decode('utf-8')
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        user = None
    chek_token = account_activation_token.check_token(user, token)
    return chek_token, user
