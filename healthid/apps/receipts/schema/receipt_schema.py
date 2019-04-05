import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.receipts.models import ReceiptTemplate, FieldSet


class ReceiptTemplateType(DjangoObjectType):
    class Meta:
        model = ReceiptTemplate


class FieldSetType(DjangoObjectType):
    class Meta:
        model = FieldSet


class Query(graphene.ObjectType):
    """
    Return a list of receipt templates
    Or a single receipt template.
    """
    receipt_templates = graphene.List(ReceiptTemplateType)
    receipt_template = graphene.Field(ReceiptTemplateType, id=graphene.String(
    ), cashier=graphene.Boolean(), discount_total=graphene.Boolean(
    ), receipt_no=graphene.Boolean(), receipt=graphene.Boolean(
    ), subtotal=graphene.Boolean(), total_tax=graphene.Boolean(
    ), amount_to_pay=graphene.Boolean(), purchase_total=graphene.Boolean(
    ), change_due=graphene.Boolean(), loyalty=graphene.Boolean(
    ), loyalty_earned=graphene.Boolean(), loyalty_balance=graphene.Boolean(
    ), barcode=graphene.Boolean(), outlet_id=graphene.Int())

    @login_required
    def resolve_receipt_templates(self, info, **kwargs):
        return ReceiptTemplate.objects.all()

    @login_required
    def resolve_receipt_template(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return ReceiptTemplate.objects.get(pk=id)

        return None
