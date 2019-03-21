from graphql_jwt.decorators import login_required
from healthid.apps.authentication.models import User, Role
from healthid.apps.authentication.auth_schema.auth_queries import RoleType
from healthid.apps.authentication.schema import UserType
from healthid.apps.authentication.utils.decorator import master_admin_required
import graphene
import os

DOMAIN = os.environ.get("DOMAIN") or os.getenv("DOMAIN")


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
                        f"Successfully updated {user_instance} to an {role_instance} role"
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
                return EditRole(success=success, role=role_instance, message=message)
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


class Mutation(graphene.ObjectType):
    create_role = CreateRole.Field()
    update_role = UpdateUserRole.Field()
    edit_role = EditRole.Field()
    delete_role = DeleteRole.Field()
