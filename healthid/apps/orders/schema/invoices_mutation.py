import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
import cloudinary
import cloudinary.api
import cloudinary.uploader
from graphql_jwt.decorators import login_required
from healthid.apps.outlets.models import Outlet
from healthid.apps.orders.models import Order
from healthid.apps.orders.models.invoices import Invoice
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.validators import validate_empty_field


class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice


class UploadInvoice(graphene.Mutation):
    """
    Uploads a new invoice for an order

    Args:
        id (int) order invoice id
        order_id (int) id of the order
        outlet_id (int) id of the outlet
        image_url (str) Invoice file to be uploaded
     returns:
        success message and details of the order and outlet
        otherwise GraphqlError instances are raised
    """
    invoice = graphene.Field(InvoiceType)
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        invoice_file = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet = get_model_object(Outlet, 'user', user)
        order_id = kwargs.get('order_id')
        order = get_model_object(Order, 'id', order_id)
        invoice_document = kwargs.get('invoice_file')
        validate_empty_field('Invoice file', invoice_document)

        invoice_exist = \
            Invoice.objects.filter(order_id=order_id).exists()

        if invoice_exist:
            raise GraphQLError('An invoice for this order already exist')

        # check if order belongs to an outlet
        if order.destination_outlet_id != outlet.id:
            raise GraphQLError('Cannot upload Invoice.'
                               ' Your outlet did not initiate this order')

        image_url = cloudinary.uploader.upload(invoice_document).get('url')

        invoice = Invoice(order_id=order.id, outlet_id=outlet.id,
                          image_url=image_url)

        with SaveContextManager(invoice) as invoice:
            return UploadInvoice(
                invoice=invoice,
                message="Invoice uploaded successfully"
            )


class Mutation(graphene.ObjectType):
    upload_invoice = UploadInvoice.Field()
