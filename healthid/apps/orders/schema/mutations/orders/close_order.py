import graphene
from graphql_jwt.decorators import login_required
from graphene_django import DjangoObjectType
from healthid.apps.orders.models.orders import SupplierOrderDetails
from healthid.apps.products.schema.product_query import BatchInfoType
from healthid.apps.products.models import BatchInfo, Quantity
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.orders.services import OrderStatusChangeService
from django.utils.dateparse import parse_date


class BatchInfoObject(graphene.InputObjectType):
    notes = graphene.String()
    date_received = graphene.String(required=True)
    delivery_promptness = graphene.Boolean(required=True)
    expiry_date = graphene.String(required=True)
    product_id = graphene.Int(required=True)
    quantity_received = graphene.Int(required=True)
    service_quality = graphene.Int(required=True)
    supplier_id = graphene.String(required=True)
    cost_per_item = graphene.Int(required=True)


class CloseOrder(graphene.Mutation):
    """
    Mutation to initiate closing an open order in the database

     arguments:
         order_id(int): name of the order to initiate

     returns:
        message(str): message containing operation response
    """
    message = graphene.String()

    class Arguments:
        supplier_order_form_id = graphene.String(required=True)
        batch_info = graphene.List(BatchInfoObject)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        supplier_order_form_id = kwargs.get("supplier_order_form_id")
        batch_info = kwargs.get("batch_info")
        supplier_order_form = get_model_object(SupplierOrderDetails,
                                               'id', supplier_order_form_id)
        if batch_info and supplier_order_form:
            for batch in batch_info:
                product_batch = BatchInfo.objects.create(
                    date_received=parse_date(batch.date_received),
                    delivery_promptness=batch.delivery_promptness,
                    expiry_date=parse_date(batch.expiry_date),
                    product_id=batch.product_id,
                    service_quality=batch.service_quality,
                    supplier_id=batch.supplier_id,
                    comment=batch.notes,
                    unit_cost=batch.cost_per_item,
                    user=user
                )
                Quantity.objects.create(
                    quantity_received=batch.quantity_received,
                    quantity_remaining=batch.quantity_received,
                    batch_id=product_batch.id,
                    is_approved=True
                )
            supplier_order_form.status = 'closed'
            supplier_order_form.save()

            return CloseOrder(message="Order has been closed successfully")
        else:
            return CloseOrder(message="You cannot close an order without batch info and supplier order id")
