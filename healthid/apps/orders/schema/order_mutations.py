import graphene
from graphql_jwt.decorators import login_required
from graphql.error import GraphQLError

from healthid.apps.orders.models.orders import Order, SupplierOrderDetails
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


class EditInitiateOrder(graphene.Mutation):
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
        """
        Mutation to edit initiated order
        """
        order_id = kwargs['order_id']
        order = get_model_object(Order, 'id', order_id)

        for(key, value) in kwargs.items():
            setattr(order, key, value)

        with SaveContextManager(order) as order:
            success = 'Order Edited Successfully!'
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


class ApproveSupplierOrder(graphene.Mutation):
    """Mutation to approve one or multiple supplier order details."""
    message = graphene.Field(graphene.String)
    supplier_order_details = graphene.List(SupplierOrderDetailsType)

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_ids = graphene.List(graphene.String)
        additional_notes = graphene.String()

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        """Approve one or multple supplier orders

        Receive a list of supplier order ids and order id.
        Make sure the supplier order details are valid and are linked to the
        recieved order.
        Approve the supplier by supplying the approver.

        Args:
            order_id (str): The id for the order
            supplier_order_ids (list: str): A list if supplier order ids
            addtional_notes (str): Additional notes

        Raises:
            GraphQLError: if supplier orders ids do not suppliers ids in the
                database

        Returns:
            supplier_order_details: A list of supplier order details
        """
        order_id = kwargs.get('order_id')
        additional_notes = kwargs.get('additional_notes')
        supplier_order_ids = kwargs.get('supplier_order_ids')

        order = get_model_object(Order, 'id', order_id)

        supplier_orders = SupplierOrderDetails.objects.filter(
            id__in=supplier_order_ids,
            order=order)

        if not supplier_orders:
            raise GraphQLError("No Supplier Order Details found matching"
                               " provided ids and order")

        user = info.context.user
        no_of_orders = len(supplier_orders)

        for supplier_order in supplier_orders:
            supplier_order.approve(user)
            if no_of_orders == 1:
                supplier_order.additional_notes = additional_notes

            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                pass

        message = "Successfully approved supplier orders"
        return ApproveSupplierOrder(message=message,
                                    supplier_order_details=supplier_orders)


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
    add_order_details = AddOrderDetails.Field()
    approve_supplier_order = ApproveSupplierOrder.Field()
    edit_initiated_order = EditInitiateOrder.Field()
