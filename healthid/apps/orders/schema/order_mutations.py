import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order, OrderDetails
from healthid.apps.outlets.models import Outlet
from healthid.utils.orders_utils.add_order_details import add_order_details
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class OrderDetailsType(DjangoObjectType):
    class Meta:
        model = OrderDetails


class InitiateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        delivery_date = graphene.Date(required=True)
        product_autofill = graphene.Boolean(required=True)
        supplier_autofill = graphene.Boolean(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        '''Mutation to initiate an order in the database
        '''
        user = info.context.user
        outlet = get_model_object(Outlet, 'user', user)
        order = Order(
            name=kwargs['name'],
            delivery_date=kwargs['delivery_date'],
            product_autofill=kwargs['product_autofill'],
            supplier_autofill=kwargs['supplier_autofill'],
            destination_outlet=outlet
        )
        with SaveContextManager(order) as order:
            success = 'Order successfully initiated!'
            return InitiateOrder(order=order, success=success)


class AddOrderDetails(graphene.Mutation):
    class Arguments:
        order_id = graphene.Int(required=True)
        products = graphene.List(graphene.Int, required=True)
        quantities = graphene.List(graphene.Int)
        suppliers = graphene.List(graphene.String)

    order_details = graphene.Field(OrderDetailsType)
    message = graphene.Field(graphene.String)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        order_id = kwargs.get('order_id')
        products = kwargs.get('products')
        quantities = kwargs.get('quantities', None)
        suppliers = kwargs.get('suppliers', None)
        order = get_model_object(Order, 'id', order_id)
        if quantities:
            params = {
                'name1': 'Quantities',
                'name2': 'Products'
            }
            add_order_details.check_list_length(products, quantities, **params)
            quantity = iter(quantities)
            order_details = \
                add_order_details.add_product_quantity(kwargs, order, quantity)
        else:
            order_details = \
                add_order_details.product_quantity_autofill(kwargs, order)
        if suppliers:
            params = {
                'name1': 'Suppliers',
                'name2': 'Products'
            }
            add_order_details.check_list_length(products, suppliers, **params)
            supplier = iter(suppliers)
            order_details = add_order_details.add_supplier(kwargs, supplier)
        else:
            order_details = add_order_details.supplier_autofill(kwargs)

        message = 'Successfully added order details!'
        return cls(order_details=order_details, message=message)


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
    add_order_details = AddOrderDetails.Field()
