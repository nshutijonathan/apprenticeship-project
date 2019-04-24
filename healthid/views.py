import io
import re

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from healthid.apps.authentication.models import User
from healthid.utils.auth_utils.tokens import account_activation_token
from healthid.utils.orders_utils import add_supplier
from healthid.utils.product_utils.handle_csv_upload import HandleCsvValidations


class HandleCSV(APIView):
    parser_classes = (MultiPartParser, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, param, format=None):
        handle_csv_object = HandleCsvValidations()
        handle_csv = handle_csv_object.handle_csv_upload
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            message = {"error": "Please upload a csv file"}
            return Response(message, status.HTTP_400_BAD_REQUEST)
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)
        if param == 'suppliers':
            add_supplier.handle_csv_upload(io_string=io_string)
            message = {"success": "Successfully added supplier(s)"}
            return Response(message, status.HTTP_201_CREATED)
        if param == 'products':
            handle_csv(io_string=io_string)
            message = {"success": "Successfully added products"}
            return Response(message, status.HTTP_201_CREATED)


class ResetPassword(APIView):
    """
    View class to perform the following functions:
    1. Receive new user password.
    2. Check that password reset token and uid hash are valid.
    2. Check that the new password is valid.
    3. Update user password.
    """

    def put(self, request, uidb64, token):
        # find the user
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64)).decode('utf-8')
            user = User.objects.get(pk=uid)

        except Exception as e:
            error = ('Something went wrong: {}'.format(e))
            return Response({"error": error},
                            status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data['user']['password']

        # validate the new password
        password_regex = '(?=.{8,100})(?=.*[A-Z])(?=.*[0-9])'
        if re.match(password_regex, new_password) is None:
            message = 'password must have at least 8 characters,'
            message += ' a number and a capital letter.'
            return Response({"error": message},
                            status=status.HTTP_400_BAD_REQUEST)

        # check validity of the token and set new password.
        if account_activation_token.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Your password was successfully reset."},
                status=status.HTTP_200_OK)
        else:
            message = "Link is invalid or is expired."
            message += " Please request another."
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )
