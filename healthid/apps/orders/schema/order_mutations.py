import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order
from healthid.apps.outlets.models import Outlet
from healthid.utils.orders_utils.add_order_details import add_order_details
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.orders_utils.supplier_order_details import \
    create_suppliers_order_details
from healthid.apps.orders.schema.order_query import \
    SupplierOrderDetailsType, OrderDetailsType, OrderType
from healthid.utils.auth_utils.decorator import user_permission


class InitiateOrder(graphene.Mutation):
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
        '''Mutation to initiate an order in the database
        '''
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
    suppliers_order_details = graphene.List(SupplierOrderDetailsType)

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
            object_list = \
                add_order_details.get_order_details(kwargs, order, quantity)
            order_details = \
                add_order_details.add_product_quantity(object_list)
        else:
            object_list = \
                add_order_details.get_order_details(kwargs, order)
            order_details = \
                add_order_details.add_product_quantity(object_list)
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
        suppliers_order_details = create_suppliers_order_details(order)

        message = 'Successfully added order details!'
        return cls(order_details=order_details,
                   message=message,
                   suppliers_order_details=suppliers_order_details)


class ApproveOrder(graphene.Mutation):
    message = graphene.Field(graphene.String)
    order = graphene.Field(OrderType)

    class Arguments:
        order_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        order = get_model_object(Order, 'id', order_id)
        user = info.context.user
        order.approve_order(user)
        with SaveContextManager(order, model=Order) as order:
            message = "Successfully approved order"
            return ApproveOrder(message=message, order=order)


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
    add_order_details = AddOrderDetails.Field()
    approve_order = ApproveOrder.Field()
