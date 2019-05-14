import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Order
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class InitiateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        destination_outlets = graphene.List(graphene.Int, required=True)
        delivery_date = graphene.Date(required=True)
        product_autofill = graphene.Boolean(required=True)
        supplier_autofill = graphene.Boolean(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        '''Mutation to initiate an order in the database
        '''
        order = Order(
            name=kwargs['name'],
            delivery_date=kwargs['delivery_date'],
            product_autofill=kwargs['product_autofill'],
            supplier_autofill=kwargs['supplier_autofill']
        )

        with SaveContextManager(order) as order:
            for outlet_id in kwargs['destination_outlets']:
                outlet = get_model_object(Outlet, 'id', outlet_id)
                order.destination_outlet.add(outlet)
                order.save()

        success = 'Order successfully initiated!'
        return InitiateOrder(order=order, success=success)


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
