import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.orders.schema.order_query import OrderType
from healthid.apps.orders.schema.mutations.orders.initiate_order import\
  InitiateOrder


class EditInitiateOrder(graphene.Mutation):
    """
    Mutation to edit an initiated order

    args:
        order_id(int): id of the initiated order to be edited
        name(str): name of the order to edit
        delivery_date(date): expected delivery date
        product_autofill(bool): toggles automatic filling in of the order's
                                products
        supplier_autofill(bool): toggles automatic filling in of the order's
                                 suppliers
        destination_outlet(int): id of the outlet destination

    returns:
        order(obj): 'Order' object detailing the edited order
        success(str): success message confirming edit of the order
    """

    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        order_id = graphene.Int(required=True)
        name = graphene.String()
        delivery_date = graphene.Date()
        product_autofill = graphene.Boolean()
        supplier_autofill = graphene.Boolean()
        destination_outlet_id = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs['order_id']
        order = get_model_object(Order, 'id', order_id)

        for(key, value) in kwargs.items():
            setattr(order, key, value)

        with SaveContextManager(order) as order:
            success = 'Order Edited Successfully!'
            return InitiateOrder(order=order, success=success)
