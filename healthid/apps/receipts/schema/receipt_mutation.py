import graphene
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from graphql_jwt.decorators import login_required
from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.receipts.schema.receipt_schema import ReceiptTemplateType
from healthid.apps.receipts.schema.template_field_mutation import (
    CreateFieldSet, UpdateFieldSet, DeleteFieldSet)


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
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            receipt_template = ReceiptTemplate()
            for(key, value) in kwargs.items():
                if (value is True or value is False) or key == 'outlet_id':
                    setattr(receipt_template, key, value)
                else:
                    raise GraphQLError(f'{key} should be true or false')
            receipt_template.save()
        except IntegrityError as e:
            raise IntegrityError(f'Integrity Error occured. {e}')
        return CreateReceiptTemplate(
            receipt_template=receipt_template
        )


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
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            id = kwargs.get('id')
            receipt_template = ReceiptTemplate.objects.get(pk=id)
            for(key, value) in kwargs.items():
                if (
                    value is True or value is False
                ) or key == 'outlet_id' or key == 'id':
                    setattr(receipt_template, key, value)
                else:
                    raise GraphQLError(f'{key} should be true or false')
            receipt_template.save()
        except ObjectDoesNotExist as e:
            raise Exception(e)

        return UpdateReceiptTemplate(
            receipt_template=receipt_template
        )


class DeleteReceiptTemplate(graphene.Mutation):
    """
    Deletes a receipt template
    """
    id = graphene.String()
    success = graphene.String()

    class Arguments:
        id = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, id):
        receipt_template = ReceiptTemplate.objects.get(pk=id)
        receipt_template.delete()

        return DeleteReceiptTemplate(
            success="Receipt template has been deleted"
        )


class Mutation(graphene.ObjectType):
    create_receipt_template = CreateReceiptTemplate.Field()
    update_receipt_template = UpdateReceiptTemplate.Field()
    delete_receipt_template = DeleteReceiptTemplate.Field()
    create_field_set = CreateFieldSet.Field()
    update_field_set = UpdateFieldSet.Field()
    delete_field_Set = DeleteFieldSet.Field()
