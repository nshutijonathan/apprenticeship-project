import graphene
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from graphql_jwt.decorators import login_required
from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.receipts.models import FieldSet
from healthid.apps.receipts.schema.receipt_schema import FieldSetType


class CreateFieldSet(graphene.Mutation):
    """
    Creates fields for template
    """
    field_set = graphene.Field(FieldSetType)

    class Arguments:
        cashier = graphene.String()
        discount_total = graphene.String()
        receipt_no = graphene.String()
        receipt = graphene.String()
        subtotal = graphene.String()
        total_tax = graphene.String()
        amount_to_pay = graphene.String()
        purchase_total = graphene.String()
        change_due = graphene.String()
        loyalty = graphene.String()
        loyalty_earned = graphene.String()
        loyalty_balance = graphene.String()
        barcode = graphene.String()
        footer = graphene.String()
        receipt_template_id = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            field_set = FieldSet()
            for(key, value) in kwargs.items():
                setattr(field_set, key, value)
            field_set.save()
        except IntegrityError as e:
            raise IntegrityError(f'Integrity Error occured. {e}')

        return CreateFieldSet(
            field_set=field_set
        )


class UpdateFieldSet(graphene.Mutation):
    """
    Updates a receipt template
    """
    field_set = graphene.Field(FieldSetType)

    class Arguments:
        id = graphene.String()
        cashier = graphene.String()
        discount_total = graphene.String()
        receipt_no = graphene.String()
        receipt = graphene.String()
        subtotal = graphene.String()
        total_tax = graphene.String()
        amount_to_pay = graphene.String()
        purchase_total = graphene.String()
        change_due = graphene.String()
        loyalty = graphene.String()
        loyalty_earned = graphene.String()
        loyalty_balance = graphene.String()
        barcode = graphene.String()
        footer = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            id = kwargs.get('id')
            field_set = FieldSet.objects.get(pk=id)
            update_values = []
            for(key, value) in kwargs.items():
                setattr(field_set, key, value)
                if key == 'id':
                    continue
                update_values.append(key)
            field_set.save(update_fields=update_values)
        except ObjectDoesNotExist as e:
            raise Exception(e)

        return UpdateFieldSet(
            field_set=field_set
        )


class DeleteFieldSet(graphene.Mutation):
    """
    Deletes fieldSet
    """
    id = graphene.String()
    success = graphene.String()

    class Arguments:
        id = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, id):
        field_set = FieldSet.objects.get(pk=id)
        field_set.delete()

        return DeleteFieldSet(
            success="FieldSet has been deleted"
        )
