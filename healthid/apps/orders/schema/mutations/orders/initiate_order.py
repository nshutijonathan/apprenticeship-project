import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.orders.schema.order_query import OrderType
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES


class InitiateOrder(graphene.Mutation):
    """
    Mutation to initiate an order in the database

    args:
        name(str): name of the order to initiate
        delivery_date(date): expected delivery date
        product_autofill(bool): toggles automatic filling in of the order's
                                products
        supplier_autofill(bool): toggles automatic filling in of the order's
                                 suppliers
        destination_outlet(int): id of the outlet destination

    returns:
        order(obj): 'Order' object detailing the created order
        success(str): success message confirming the initiated order
    """

    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        delivery_date = graphene.Date(required=True)
        product_autofill = graphene.Boolean(required=True)
        supplier_autofill = graphene.Boolean(required=True)
        destination_outlet = graphene.Int(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        outlet = get_model_object(
            Outlet, 'id', kwargs.get('destination_outlet'))
        order = Order(
            name=kwargs['name'],
            delivery_date=kwargs['delivery_date'],
            product_autofill=kwargs['product_autofill'],
            supplier_autofill=kwargs['supplier_autofill'],
            destination_outlet=outlet
        )
        with SaveContextManager(order) as order:
            success = ORDERS_SUCCESS_RESPONSES["order_initiation_success"]
            return InitiateOrder(order=order, success=success)
