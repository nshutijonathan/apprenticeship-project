from os import environ, getenv

import cloudinary
import cloudinary.api
import cloudinary.uploader
import graphene
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import Role, User
from healthid.apps.authentication.schema.auth_queries import RoleType, UserType
from healthid.apps.authentication.schema.login_mutation import LoginUser
from healthid.apps.authentication.schema.reset_password_mutation import \
    ResetPassword
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils import user_update_instance
from healthid.utils.auth_utils.admin_validation import validate_instance
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.auth_utils.password_generator import generate_password
from healthid.utils.auth_utils.tokens import account_activation_token
from healthid.utils.auth_utils.validations import ValidateUser
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.messages.authentication_responses import (
    AUTH_SUCCESS_RESPONSES,
    AUTH_ERROR_RESPONSES)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class PasswordInput(graphene.InputObjectType):
    new_password = graphene.String()
    old_password = graphene.String()


class RoleInput(graphene.InputObjectType):
    """
        Specifying the data types of the Role Input
    """

    id = graphene.String()
    name = graphene.String()


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
    verification_link = graphene.Field(graphene.String)

    def mutate(self, info, email, password, mobile_number):
        validate_fields = ValidateUser().validate_user_fields(
            email, password, mobile_number)
        try:
            user = User.objects.create_user(**validate_fields)
            role = get_model_object(Role, 'name', 'Master Admin')
            user.set_password(password)
            user.role = role
            user.save()
            # account verification
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(
                user.pk)).decode()
            to_email = [
                user.email
            ]
            email_verify_template = \
                'email_alerts/authentication/verification_email.html'
            subject = 'Account Verification'
            context = {
                'template_type': 'Verify your email',
                'small_text_detail': 'Thank you for '
                                     'creating a HealthID account. '
                                     'Please verify your email '
                                     'address to set up your account.',
                'email': user.email,
                'domain': DOMAIN,
                'uid': uid,
                'token': token,
            }
            send_mail = SendMail(
                email_verify_template, context, subject, to_email)
            send_mail.send()
            registration_message =\
                AUTH_SUCCESS_RESPONSES["registration_success"]
            verification_message = AUTH_SUCCESS_RESPONSES["email_verification"]

            success = [
                registration_message + verification_message
            ]
            verification_link = f"{DOMAIN}/healthid/activate/{uid}/{token}"
            return RegisterUser(success=success, user=user,
                                verification_link=verification_link)
        except Exception as e:
            errors = ["Something went wrong: {}".format(e)]
            return RegisterUser(errors=errors)


class AddUser(graphene.Mutation):
    """
        Mutation to register a user.
    """
    user = graphene.Field(UserType)
    verification_link = graphene.Field(graphene.String)

    class Arguments:
        outlet_id = graphene.List(graphene.String, required=True)
        email = graphene.String(required=True)
        mobile_number = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        profile_image = graphene.String()
        job_title = graphene.String()
        starting_date = graphene.String()
        birthday = graphene.String()
        role_id = graphene.String(required=True)

    success = graphene.List(graphene.String)
    errors = graphene.List(graphene.String)

    @login_required
    @user_permission()
    @user_update_instance
    def mutate(self, info, **kwargs):
        password = generate_password()
        email = kwargs.get('email')
        mobile_number = kwargs.get('mobile_number')
        outlet = kwargs.get('outlet_id')
        role_id = kwargs.get('role_id')
        profile_image = kwargs.get('profile_image')

        data = {
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'username': kwargs.get('username'),
            'job_title': kwargs.get('job_title'),
            'starting_date': kwargs.get('starting_date'),
            'birthday': kwargs.get('birthday'),
        }

        role_instance = get_model_object(Role, 'id', role_id)
        try:
            user_fields = {
                "email": email,
                "password": password,
                "mobile_number": mobile_number
            }
            user = User.objects.create_user(**user_fields)
            user_update_instance.add_user(user, **data)
            user.role = role_instance
            for outlet_id in outlet:
                outlet_instance = get_model_object(Outlet, 'id', outlet_id)
                business_instance = outlet_instance.business
                business_instance.user.add(user)
                user.users.add(outlet_instance)
            if profile_image:
                user.profile_image = \
                    cloudinary.uploader.upload(profile_image).get('url')
            user.save()
            # Email verification
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(
                user.pk)).decode()
            to_email = [
                user.email
            ]
            email_verify_template = \
                'email_alerts/authentication/add_user_verification.html'
            subject = 'Account Verification'
            context = {
                'template_type': 'Verify your email',
                'small_text_detail': ' A HealthID account has been created '
                                     'for you. Please verify your email '
                                     'address to set up your account.',
                'email': email,
                'domain': DOMAIN,
                'uid': uid,
                'token': token,
                'password': password
            }
            send_mail = SendMail(
                email_verify_template, context, subject, to_email)
            send_mail.send()
            verification_link = f"{DOMAIN}/healthid/activate/{uid}/{token}"
            add_user_message =\
                AUTH_SUCCESS_RESPONSES["adding_new_user"].format(user.username)
            success = [
                add_user_message
            ]

            return AddUser(success=success, user=user,
                           verification_link=verification_link)
        except Exception as e:
            errors = ['Something went wrong: {}'.format(e)]
            return AddUser(errors=errors)


class AdminUpdateUserDetails(graphene.Mutation):
    """
        Admin update some specific fields in the user profile
    """

    class Arguments:
        id = graphene.String(required=True)
        job_title = graphene.String()
        starting_date = graphene.String()
        email = graphene.String(required=True)
        mobile_number = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        profile_image = graphene.String()
        birthday = graphene.String()

    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @user_update_instance
    @user_permission()
    def mutate(self, info, **kwargs):
        profile_image = kwargs.get('profile_image')
        data = {
            'email': kwargs.get('email'),
            'mobile_number': kwargs.get('mobile_number'),
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'username': kwargs.get('username'),
            'job_title': kwargs.get('job_title'),
            'starting_date': kwargs.get('starting_date'),
            'birthday': kwargs.get('birthday'),
        }
        user_id = kwargs.get('id')
        user = get_model_object(User, 'id', user_id)
        user_update_instance.add_user(user, **data)
        if profile_image:
            user.profile_image = \
                cloudinary.uploader.upload(profile_image).get('url')
        user.save()
        update_message = SUCCESS_RESPONSES["update_success"]
        message = [
            update_message.format(user.username)
        ]
        return AdminUpdateUserDetails(message=message, user=user)


class UpdateUserDetails(graphene.Mutation):
    """
    mutation to update user details
    """

    class Arguments:
        mobile_number = graphene.String()
        password = graphene.List(PasswordInput)
        username = graphene.String()
        profile_image = graphene.String()
        email = graphene.String()
        email_notification_permissions = graphene.Boolean()

    user = graphene.Field(UserType)
    error = graphene.Field(graphene.String)
    success = graphene.Field(graphene.String)

    @login_required
    @user_update_instance
    def mutate(self, info, **kwargs):
        user = info.context.user
        if kwargs.get('password') is not None:
            password_input = kwargs.get('password')
            old_password = password_input[0].old_password
            check_old_password = user.check_password(old_password)
            if not check_old_password:
                error_message = AUTH_ERROR_RESPONSES["password_match_error"]
                raise GraphQLError(error_message)
        if kwargs.get('email') is not None:
            email = kwargs.get('email')
            if User.objects.filter(email=email):
                email_error = AUTH_ERROR_RESPONSES["email_duplicate_error"]
                raise GraphQLError(email_error)

        user_update_instance.update_user(user, **kwargs)
        success = SUCCESS_RESPONSES["update_success"].format(user.username)
        return UpdateUserDetails(
            success=success, error=None, user=user)


class CreateRole(graphene.Mutation):
    """
        Role creation Mutation
    """

    class Arguments:
        input = RoleInput(required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, input=None):
        success = True
        errors = ["name", "Role Field is empty"]
        if input.name != "":
            role = Role(name=input.name)
            with SaveContextManager(role, model=Role):
                message = [f"Successfully created a role: {input.name}"]
                return CreateRole(success=success, role=role, message=message)
        return CreateRole(errors=errors)


class UpdateUserRole(graphene.Mutation):
    """
      This class updates the User role
    """

    class Arguments:
        role_id = graphene.String(required=True)
        user_id = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, **kwargs):
        user_id = kwargs.get('user_id')
        role_id = kwargs.get('role_id')
        user_instance = get_model_object(User, 'id', user_id)
        role_instance = get_model_object(Role, 'id', role_id)
        admin_instance = get_model_object(Role, 'name', 'Master Admin')
        business_users = User.objects.filter(
            business__user=user_instance)
        business_admin = business_users.filter(
            role=admin_instance).count()
        if user_instance.role == role_instance:
            role_error = AUTH_ERROR_RESPONSES["assigning_user_roles"]
            raise GraphQLError(role_error)
        if business_admin == 1 \
                and role_instance != admin_instance:
            downgrade_error = AUTH_ERROR_RESPONSES["downgrade_user"]
            raise GraphQLError(downgrade_error)
        user_instance.role = role_instance
        user_instance.save()
        message = [
            f"Successfully updated {user_instance}"
            f" to a {role_instance} role"
        ]
        return UpdateUserRole(
            user=user_instance,
            message=message)


class EditRole(graphene.Mutation):
    """
        Role Edit Mutation
    """

    class Arguments:
        id = graphene.String(required=True)
        input = RoleInput(required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, id, input=None):
        success = False
        role_instance = get_model_object(Role, 'id', id)
        role_instance.name = input.name
        with SaveContextManager(role_instance, model=Role):
            success = True
            edit_success = SUCCESS_RESPONSES["update_success"]
            message = [edit_success.format(role_instance.name)]
            return EditRole(
                success=success, role=role_instance, message=message
            )


class DeleteRole(graphene.Mutation):
    """
        Role Delete Mutation
    """

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, id):
        role_instance = get_model_object(Role, 'id', id)
        success = True
        message =\
            SUCCESS_RESPONSES["deletion_success"].format(role_instance.name)
        role_instance.delete()
        return DeleteRole(success=success, message=message)


class UpdateAdminUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Field(graphene.String)

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        secondary_email = graphene.String()
        secondary_phone_number = graphene.String()

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, **kwargs):
        user = info.context.user
        validated_fileds = validate_instance.validate_admin_fields(**kwargs)
        user_instance = get_model_object(User, 'id', user.id)
        for (key, value) in validated_fileds.items():
            if key is not None:
                setattr(user_instance, key, value)
        user_instance.save()
        success = SUCCESS_RESPONSES["update_success"].format("Admin Profile")
        return UpdateAdminUser(user=user_instance, success=success)


class Mutation(graphene.ObjectType):
    add_user = AddUser.Field()
    create_user = RegisterUser.Field()
    update_user = UpdateUserDetails.Field()
    create_role = CreateRole.Field()
    update_role = UpdateUserRole.Field()
    edit_role = EditRole.Field()
    delete_role = DeleteRole.Field()
    update_admin_user = UpdateAdminUser.Field()
    admin_update_user = AdminUpdateUserDetails.Field()
    login_user = LoginUser.Field()
    reset_password = ResetPassword.Field()
