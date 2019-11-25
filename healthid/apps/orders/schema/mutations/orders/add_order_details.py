import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order
from healthid.utils.orders_utils.add_order_details import add_order_details
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.orders_utils.supplier_order_details import \
    create_suppliers_order_details
from healthid.apps.orders.schema.order_query import \
    SupplierOrderDetailsType, OrderDetailsType
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES


class AddOrderDetails(graphene.Mutation):
    """
    Mutation that creates a new record in the 'OrderDetails' model.
    Validates the length of the input argument lists and
    checks for duplicate model entries.

    Arguments:
        order_id(int): id of the initiated order to be updated
        products(list): products to be added
        quantities(list): quantities for each product
        suppliers(list): suppliers of each product
        supplier_autofill(bool): toggles automatic filling in of the order's
                                 suppliers
        destination_outlet(int): id of the outlet destination

    Returns:
        order_details(obj): latest order detail created
        message(str): success message
        suppliers_order_details(list): suppliers order details for a given
                                        order
    """

    class Arguments:
        order_id = graphene.Int(required=True)
        products = graphene.List(graphene.Int, required=True)
        quantities = graphene.List(graphene.Int)
        suppliers = graphene.List(graphene.String)
        prices = graphene.List(graphene.String)
        cost_per_items = graphene.List(graphene.String)

    order_details = graphene.Field(OrderDetailsType)
    message = graphene.Field(graphene.String)
    suppliers_order_details = graphene.List(SupplierOrderDetailsType)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        order_id = kwargs.get('order_id')
        products = kwargs.get('products')
        quantities = kwargs.get('quantities', None)
        cost_per_items = kwargs.get('cost_per_items', None)
        prices = kwargs.get('prices', None)
        suppliers = kwargs.get('suppliers', None)
        order = get_model_object(Order, 'id', order_id)

        if quantities and prices and cost_per_items:
            params = {
                'name1': 'Quantities',
                'name2': 'Products'
            }
            params2 = {
                'name1': 'Prices',
                'name2': 'Products'
            }
            params3 = {
                'name1': 'CostPerItems',
                'name2': 'Products'
            }
            add_order_details.check_list_length(products, quantities, **params)
            add_order_details.check_list_length(products, prices, **params2)
            add_order_details.check_list_length(
                products, cost_per_items, **params3
            )
            quantity = iter(quantities)
            price = iter(prices)
            cost_per_item = iter(cost_per_items)
            object_list = add_order_details.get_order_details(
                kwargs, order, quantity, price, cost_per_item
            )
        elif quantities:
            params = {
                'name1': 'Quantities',
                'name2': 'Products'
            }
            add_order_details.check_list_length(products, quantities, **params)
            quantity = iter(quantities)
            object_list = add_order_details.get_order_details(
                kwargs, order, quantity
            )
        else:
            object_list = \
                add_order_details.get_order_details(kwargs, order)

        if suppliers:
            params = {
                'name1': 'Suppliers',
                'name2': 'Products'
            }
            add_order_details.check_list_length(products, suppliers, **params)
            supplier = iter(suppliers)
            order_details = add_order_details.add_supplier(
                kwargs,
                supplier,
                object_list
            )
        else:
            order_details = add_order_details.supplier_autofill(
                kwargs,
                object_list
            )

        message = ORDERS_SUCCESS_RESPONSES["order_addition_success"]
        suppliers_order_details = create_suppliers_order_details(order)
        return cls(order_details=order_details,
                   message=message,
                   suppliers_order_details=suppliers_order_details)
