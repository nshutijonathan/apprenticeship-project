import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.outlets.models import Outlet
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.register.models import Register
from healthid.apps.register.schema.register_schema import RegisterType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.messages.register_responses import REGISTER_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class RegisterInput(graphene.InputObjectType):

    id = graphene.String()
    name = graphene.String()


class CreateRegister(graphene.Mutation):
    """
    This Creates a register
    """
    register = graphene.Field(RegisterType)

    class Arguments:
        name = graphene.String(required=True)
        outlet_id = graphene.Int(required=True)
        receipt_id = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        register_name = kwargs.get('name')
        outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        receipt_template = get_model_object(
            ReceiptTemplate, 'id', kwargs.get('receipt_id'))
        if register_name.strip() != "":
            register = Register(
                name=register_name, outlet_id=outlet.id,
                receipt_id=receipt_template.id)
            with SaveContextManager(register, model=Register) as register:
                return CreateRegister(register=register)

        raise GraphQLError(
              REGISTER_ERROR_RESPONSES[
                 "invalid_register_name_error"].format(register_name))


class UpdateRegister(graphene.Mutation):
    """
    This Updates a register
    """
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)
    success = graphene.Boolean()
    register = graphene.Field(RegisterType)

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, id, name):
        register = get_model_object(Register, 'id', id)
        if name.strip() != "":
            register.name = name
            register.save()
            success = SUCCESS_RESPONSES["update_success"].format("Register")
            return UpdateRegister(success=success, register=register)
        raise GraphQLError(
            REGISTER_ERROR_RESPONSES[
                "invalid_register_name_error"].format(name))


class DeleteRegister(graphene.Mutation):
    """
    This Deletes a register
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        register = get_model_object(Register, 'id', id)
        register.delete(user)
        return DeleteRegister(
            success=SUCCESS_RESPONSES[
                    "deletion_success"].format("Register"))


class Mutation(graphene.ObjectType):
    create_register = CreateRegister.Field()
    delete_register = DeleteRegister.Field()
    update_register = UpdateRegister.Field()
