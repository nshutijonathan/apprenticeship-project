import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.receipts.schema.receipt_schema import ReceiptTemplateType
from healthid.apps.receipts.schema.template_field_mutation import (
    CreateFieldSet, DeleteFieldSet, UpdateFieldSet)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.receipts_responses import RECEIPTS_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class CreateReceiptTemplate(graphene.Mutation):
    """
    Creates a receipt template
    """
    receipt_template = graphene.Field(ReceiptTemplateType)

    class Arguments:
        cashier = graphene.Boolean()
        discount_total = graphene.Boolean()
        receipt_no = graphene.Boolean()
        receipt = graphene.Boolean()
        subtotal = graphene.Boolean()
        total_tax = graphene.Boolean()
        amount_to_pay = graphene.Boolean()
        purchase_total = graphene.Boolean()
        change_due = graphene.Boolean()
        loyalty = graphene.Boolean()
        loyalty_earned = graphene.Boolean()
        loyalty_balance = graphene.Boolean()
        barcode = graphene.Boolean()
        outlet_id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        receipt_template = ReceiptTemplate()
        for(key, value) in kwargs.items():
            if (value is True or value is False) or key == 'outlet_id':
                setattr(receipt_template, key, value)
            else:
                raise GraphQLError(
                      RECEIPTS_ERROR_RESPONSES["key_error"].format(key))
        with SaveContextManager(receipt_template) as receipt_template:
            return CreateReceiptTemplate(receipt_template=receipt_template)


class UpdateReceiptTemplate(graphene.Mutation):
    """
    Updates a receipt template
    """
    receipt_template = graphene.Field(ReceiptTemplateType)

    class Arguments:
        id = graphene.String()
        cashier = graphene.Boolean()
        discount_total = graphene.Boolean()
        receipt_no = graphene.Boolean()
        receipt = graphene.Boolean()
        subtotal = graphene.Boolean()
        total_tax = graphene.Boolean()
        amount_to_pay = graphene.Boolean()
        purchase_total = graphene.Boolean()
        change_due = graphene.Boolean()
        loyalty = graphene.Boolean()
        loyalty_earned = graphene.Boolean()
        loyalty_balance = graphene.Boolean()
        barcode = graphene.Boolean()
        outlet_id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        receipt_template = get_model_object(ReceiptTemplate, 'id', id)
        for(key, value) in kwargs.items():
            if type(value) is bool or key in ('outlet_id', 'id'):
                setattr(receipt_template, key, value)
            else:
                raise GraphQLError(
                      RECEIPTS_ERROR_RESPONSES["key_error"].format(key))
        receipt_template.save()

        return UpdateReceiptTemplate(receipt_template=receipt_template)


class DeleteReceiptTemplate(graphene.Mutation):
    """
    Deletes a receipt template
    """
    id = graphene.String()
    success = graphene.String()

    class Arguments:
        id = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        receipt_template = get_model_object(ReceiptTemplate, 'id', id)
        receipt_template.delete(user)

        return DeleteReceiptTemplate(
            success=SUCCESS_RESPONSES[
                    "deletion_success"].format("Receipt template")
        )


class Mutation(graphene.ObjectType):
    create_receipt_template = CreateReceiptTemplate.Field()
    update_receipt_template = UpdateReceiptTemplate.Field()
    delete_receipt_template = DeleteReceiptTemplate.Field()
    create_field_set = CreateFieldSet.Field()
    update_field_set = UpdateFieldSet.Field()
    delete_field_Set = DeleteFieldSet.Field()
