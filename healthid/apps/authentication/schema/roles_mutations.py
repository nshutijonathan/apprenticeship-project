from os import environ, getenv

from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import Role, User
from healthid.apps.authentication.schema.auth_queries import RoleType, UserType
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)

from healthid.utils.messages.authentication_responses import (
    AUTH_ERROR_RESPONSES)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
import graphene
DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class RoleInput(graphene.InputObjectType):
    """
        Specifying the data types of the Role Input
    """

    id = graphene.String()
    name = graphene.String()


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
        errors = ["Role Field is empty"]
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


class RoleInput(graphene.InputObjectType):
    """
        Specifying the data types of the Role Input
    """

    id = graphene.String()
    name = graphene.String()


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


class Mutation(graphene.ObjectType):
    create_role = CreateRole.Field()
    update_role = UpdateUserRole.Field()
    edit_role = EditRole.Field()
    delete_role = DeleteRole.Field()
