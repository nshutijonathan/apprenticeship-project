from os import environ, getenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import graphene
from graphql import GraphQLError
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from graphql_jwt.decorators import login_required
from healthid.apps.authentication.models import Role, User
from healthid.apps.outlets.models import Outlet
from healthid.apps.authentication.utils import user_update_instance
from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.authentication.utils.tokens import account_activation_token
from healthid.apps.authentication.utils.validations import ValidateUser
from healthid.apps.authentication.utils.admin_validation \
    import validate_instance

from .auth_queries import RoleType, UserType
from healthid.apps.authentication.utils.password_generator \
    import generate_password
from healthid.apps.authentication.querysets.role_query \
    import ModelQuery
from healthid.apps.authentication.querysets.user_query \
    import UserModelQuery

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

    def mutate(self, info, email, password, mobile_number):
        validate_fields = ValidateUser().validate_user_fields(
            email, password, mobile_number)
        try:
            user = User.objects.create_user(**validate_fields)
            role = ModelQuery().query_role_name('Master Admin')
            user.set_password(password)
            user.role = role
            user.save()
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
                "You have successfully registered with healthID."
                " Please check your email to verify your account"
            ]
            return RegisterUser(success=success, user=user)
        except Exception as e:
            errors = ["Something went wrong: {}".format(e)]
            return RegisterUser(errors=errors)


class AddUser(graphene.Mutation):
    """
        Mutation to register a user.
    """
    user = graphene.Field(UserType)

    class Arguments:
        outlet_id = graphene.List(graphene.String)
        email = graphene.String(required=True)
        mobile_number = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        profile_image = graphene.String()
        job_title = graphene.String()
        starting_date = graphene.String()
        birthday = graphene.String()
        role_id = graphene.String()

    success = graphene.List(graphene.String)
    errors = graphene.List(graphene.String)

    @login_required
    @master_admin_required
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

        role_instance = ModelQuery().query_role_id(role_id)
        try:
            user_fields = {
                "email": email,
                "password": password,
                "mobile_number": mobile_number
            }
            user = User.objects.create_user(**user_fields)
            user_update_instance.add_user(user, **data)
            user.role = role_instance
            for i in outlet:
                outlet_instance = Outlet.objects.get(id=i)
                user.users.add(outlet_instance)
            if profile_image:
                user.profile_image = \
                    cloudinary.uploader.upload(profile_image).get('url')
            user.save()
            # Email verification
            token = account_activation_token.make_token(user)
            html_body = render_to_string(
                'emails/add_user_verification.html', {
                    'email': email,
                    'domain': DOMAIN,
                    'uid': urlsafe_base64_encode(force_bytes(
                        user.pk)).decode(),
                    'token': token,
                    'password': password
                })
            msg = EmailMessage(
                subject='Account Verification',
                body=html_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email])
            msg.content_subtype = 'html'
            msg.send()
            success = [
                'message',
                'You have successfully registered a User.'
            ]

            return AddUser(success=success, user=user)
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
    @master_admin_required
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
        user = UserModelQuery().query_user_id(user_id)
        user_update_instance.add_user(user, **data)
        if profile_image:
            user.profile_image = \
                cloudinary.uploader.upload(profile_image).get('url')
        user.save()
        message = [
            'message',
            'You have successfully updated this User.'
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
                raise GraphQLError('password does not match old password!')
        if kwargs.get('email') is not None:
            email = kwargs.get('email')
            if User.objects.filter(email=email):
                raise GraphQLError('email has already been registered.')

        user_update_instance.update_user(user, **kwargs)
        success = "user successfully updated"
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
    @master_admin_required
    def mutate(root, info, input=None):
        success = True
        errors = ["name", "Role Field is empty"]
        if input.name != "":
            try:
                role = Role.objects.create(name=input.name)
                message = [f"Successfully created a role: {role}"]
                return CreateRole(success=success, role=role, message=message)
            except Exception as e:
                errors = ["Something went wrong: {}".format(e)]
                return CreateRole(success=False, errors=errors)
        return CreateRole(errors=errors)


class UpdateUserRole(graphene.Mutation):
    """
      This class updates the User role
    """

    class Arguments:
        id = graphene.String(required=True)
        input = RoleInput(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @master_admin_required
    def mutate(root, info, id, input=None):
        success = False
        if id is None:
            errors = ["id", "User Id is empty"]
            return UpdateUserRole(success, errors=errors)
        user_instance = User.objects.get(id=id)
        if user_instance is None:
            errors = ["user", "User does not exist"]
            return UpdateUserRole(success, errors=errors)
        if input.name != "":
            try:
                role_instance = Role.objects.get(name=input.name)
                if role_instance:
                    success = True
                    user_instance.role = role_instance
                    user_instance.save()
                    message = [
                        f"Successfully updated {user_instance}"
                        " to an {role_instance} role"
                    ]
                    return UpdateUserRole(
                        success=success, user=user_instance, message=message
                    )
                return UpdateUserRole(success=success, user=None)
            except Exception as e:
                errors = ["Something went wrong: {}".format(e)]
                return UpdateUserRole(success=False, errors=errors)
        errors = ["name", "Role Field is empty"]
        return UpdateUserRole(success=False, errors=errors)


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
    @master_admin_required
    def mutate(root, info, id, input=None):
        success = False
        try:
            role_instance = Role.objects.get(id=id)
            if role_instance:
                success = True
                role_instance.name = input.name
                role_instance.save()
                message = [f"Successfully Edited the role"]
                return EditRole(
                    success=success,
                    role=role_instance,
                    message=message
                )
        except Exception as e:
            errors = ["Something went wrong: {}".format(e)]
            return EditRole(success=success, role=None, errors=errors)


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
    @master_admin_required
    def mutate(root, info, id):
        success = False
        try:
            role_instance = Role.objects.get(id=id)
            if role_instance:
                success = True
                message = [f"Role {role_instance.name} has been deleted"]
                role_instance.delete()
                return DeleteRole(success=success, message=message)
        except Exception as e:
            errors = ["Something went wrong: {}".format(e)]
            return DeleteRole(success=success, role=None, errors=errors)


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
    @master_admin_required
    def mutate(root, info, **kwargs):
        user = info.context.user
        validated_fileds = validate_instance.validate_admin_fields(**kwargs)
        try:
            user_instance = User.objects.get(id=user.id)
        except Exception as e:
            raise GraphQLError(str(e))
        for (key, value) in validated_fileds.items():
            if key is not None:
                setattr(user_instance, key, value)
        user_instance.save()
        success = 'admin profile successfully updated'
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
