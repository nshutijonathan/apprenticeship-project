import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import (Order, SupplierOrderDetails,
                                                OrderDetails)
from healthid.apps.outlets.models import Outlet
from healthid.utils.orders_utils.add_order_details import add_order_details
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.orders_utils.supplier_order_details import \
    create_suppliers_order_details
from healthid.apps.orders.schema.order_query import \
    SupplierOrderDetailsType, OrderDetailsType, OrderType
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.apps.orders.services import (SupplierOrderDetailsFetcher,
                                           SupplierOrderEmailSender,
                                           SupplierOrderDetailsApprovalService)


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


class ApproveSupplierOrder(graphene.Mutation):
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

    message = graphene.Field(graphene.String)
    supplier_order_details = graphene.List(SupplierOrderDetailsType)

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_ids = graphene.List(graphene.String)
        additional_notes = graphene.String()

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        additional_notes = kwargs.get('additional_notes', None)
        supplier_order_ids = kwargs.get('supplier_order_ids')

        user = info.context.user
        orders_fetcher = SupplierOrderDetailsFetcher(order_id,
                                                     supplier_order_ids)
        supplier_orders = orders_fetcher.fetch()
        approval_service = SupplierOrderDetailsApprovalService(
            supplier_orders, user, additional_notes)
        message = approval_service.approve()
        return ApproveSupplierOrder(message=message,
                                    supplier_order_details=supplier_orders)


class SendSupplierOrderEmails(graphene.Mutation):
    """Send Supplier Order Emails to suppliers

    Send a PDF supplier order form to the supplier listing
    all ordered items.

    Args:
        supplier_order_ids: A list of supplier order ids

    Returns:
        message: a return message
    """
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_ids = graphene.List(graphene.String,
                                           required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        supplier_order_ids = kwargs.get('supplier_order_ids')

        details_fetcher = SupplierOrderDetailsFetcher(order_id,
                                                      supplier_order_ids)
        email_sender = SupplierOrderEmailSender(details_fetcher.fetch())
        message = email_sender.send()
        return SendSupplierOrderEmails(message=message)


class MarkSupplierOrderAsSent(graphene.Mutation):
    """Mark Supplier Order Details as sent

    Mark BooleanField marked_as_sent

    Args:
        supplier_order_ids: A list of supplier order ids

    Returns:
        message: a return messae.
    """
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_ids = graphene.List(graphene.String,
                                           required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        supplier_order_ids = kwargs.get('supplier_order_ids')
        details_fetcher = SupplierOrderDetailsFetcher(order_id,
                                                      supplier_order_ids)
        supplier_orders = details_fetcher.fetch()
        ids = list()
        for supplier_order in supplier_orders:
            supplier_order.marked_as_sent = True
            ids.append(supplier_order.id)
            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                pass

        message = ORDERS_SUCCESS_RESPONSES[
            "supplier_order_marked_closed"].format(
                ",".join(id for id in ids))
        return MarkSupplierOrderAsSent(message=message)


class DeleteOrderDetail(graphene.Mutation):
    """
    Mutation that deletes one or more records in the 'OrderDetails' model.

    Arguments:
        kwargs(dict): contains the id of the 'OrderDetails'
                        record to be deleted.

    Returns:
        message(str): confirms successful record(s) deletion
    """

    class Arguments:
        order_detail_id = graphene.List(graphene.String, required=True)

    message = graphene.Field(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        order_detail_id = kwargs.get('order_detail_id')
        success_message = SUCCESS_RESPONSES["deletion_success"].format(
            "Product details"
            )
        for order_detail_id in order_detail_id:
            removed_product = get_model_object(
                OrderDetails,
                'id',
                order_detail_id
            )
            removed_product.hard_delete()
        return DeleteOrderDetail(message=success_message)


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
    add_order_details = AddOrderDetails.Field()
    approve_supplier_order = ApproveSupplierOrder.Field()
    edit_initiated_order = EditInitiateOrder.Field()
    delete_order_detail = DeleteOrderDetail.Field()
    send_supplier_order_emails = SendSupplierOrderEmails.Field()
    mark_supplier_order_as_sent = MarkSupplierOrderAsSent.Field()
