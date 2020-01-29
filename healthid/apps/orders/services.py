"""Service objects that implement business logic."""
from graphql.error import GraphQLError

from healthid.apps.orders.models import \
    Order, SupplierOrderDetails, SuppliersContacts
from healthid.utils.app_utils.send_mail import SendMail
from healthid.apps.orders.models.orders import AutoFillProducts
from healthid.utils.app_utils.database import (get_model_object,
                                               SaveContextManager)
from healthid.utils.messages.orders_responses import (
    ORDERS_SUCCESS_RESPONSES, ORDERS_ERROR_RESPONSES)


class SupplierOrderDetailsFetcher:
    """Defines an object that fetches supplier order details

    Args:
        order_id(String): The id of an order
        supplier_order_details_ids (List): a list of supplier order ids
    """

    def __init__(self, order_id, supplier_order_details_ids):
        self.order_id = order_id
        self.supplier_order_details_ids = supplier_order_details_ids

    def fetch(self):
        """Get Supplier Order Details

        Get all supplier order details belong to provided order and match
        the provided ids.

        Returns:
            (Obj:) QuerySet object of supplier order details
        """
        order = get_model_object(Order, 'id', self.order_id)
        results = SupplierOrderDetails.objects.all()
        results = results.filter(
            id__in=self.supplier_order_details_ids, order=order)
        if not results:
            raise ValueError("No supplier Order Details found matching "
                             "provided ids and Order")
        return results


class SupplierOrderEmailSender:
    """Defines an object that sends order emails to suppliers.

    Args:
        supplier_order_details (QuerySet): a queryset for
        supplier order details
    """

    def __init__(self, supplier_order_details):
        self.supplier_order_details = supplier_order_details

    def send(self):
        detail_ids = list()
        for detail in self.supplier_order_details:
            supplier = SuppliersContacts.objects.filter(
                supplier_id=detail.supplier.id).first()
            email = supplier.email if supplier else None
            self._send_single_email(email, detail)
            detail.status = detail.OPEN
            detail_ids.append(detail.id)
        return ORDERS_SUCCESS_RESPONSES["supplier_order_email_success"].format(
            ', '.join([id for id in detail_ids]))

    @staticmethod
    def _send_single_email(email, detail):
        context = {'detail': detail}
        mail = SendMail(
            to_email=[email],
            subject='Supplier Order Form Email',
            template='email_alerts/orders/supplier_order_email.html',
            context=context
        )
        mail.send()


class SupplierOrderDetailsApprovalService:
    """A service object that approves supplier order details.

    Approve a supplier order detail indicating the approver.
    Change the status of the supplier order detail to "Open"

    Args:
        supplier_order_detail: a supplier order details object
        user: a User object

    Returns:
        (Obj:) supplier_order_detail
    """

    def __init__(self, supplier_orders, user, additional_notes=None):
        self.supplier_orders = supplier_orders
        self.user = user
        self.additional_notes = additional_notes

    def approve(self):
        """Approve multiple supplier order details.

        Returns:
            message: A return message
        """
        no_of_orders = len(self.supplier_orders)

        ids = list()
        for supplier_order in self.supplier_orders:
            self._approve_single_detail(supplier_order, self.user)
            if no_of_orders == 1:
                supplier_order.additional_notes = self.additional_notes

            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                ids.append(supplier_order.id)

        return ORDERS_SUCCESS_RESPONSES[
            "supplier_order_approval_success"].format(
                ', '.join([id for id in ids]))

    @staticmethod
    def _approve_single_detail(supplier_order, user):
        """Approve single a supplier order.

        Returns:
            (Obj): SupplierOrderDetails instance
        """
        supplier_order.approved_by = user
        supplier_order.approved = True
        return supplier_order


class SupplierOrderStatusChangeService:
    """A service object that chnages supplier order details
    status to approved.

    Approve a supplier order detail indicating the approver.
    Change the status of the supplier order detail to "Approved"

    Args:
        supplier_order_detail: a supplier order id

    Returns:
        (Obj:) supplier_order_detail
    """

    def __init__(self, supplier_order_details_id, user):
        self.user = user
        self.supplier_order_details_id = supplier_order_details_id

    def change_status(self):
        if self.supplier_order_details_id[0] == "":
            raise GraphQLError(ORDERS_ERROR_RESPONSES[
                'none_supplier_order_id'])
        results = SupplierOrderDetails.objects.all()
        supplier_order = results.filter(
            id__in=self.supplier_order_details_id).first()
        if supplier_order:
            if supplier_order.approved is not True:
                raise GraphQLError(ORDERS_ERROR_RESPONSES[
                    'supplier_order_not_approved'].format('approved'))
            supplier_order.status = 'approved'
            supplier_order.approved_by = self.user
            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                return ORDERS_SUCCESS_RESPONSES[
                    "supplier_order_mark_status"
                ].format(self.supplier_order_details_id)
        raise GraphQLError(ORDERS_ERROR_RESPONSES[
            'no_supplier_order_id'].format(self.supplier_order_details_id))


class OrderStatusChangeService:
    """A service object that changes order status

    - once an order has been initiated, system should give the order a status of
        `Incomplete order form`
    - when order list has been populated and generated, the system should give the
        supplier order a status of `waiting for order to be placed`
    - when the order has been placed and auto-sent to the supplier, the system should
        give the supplier order a status of `Open`
    - when all ordered products have been assigned batches and the user has closed the
        order, system should give the supplier order a status of `Closed`

    Args:
        order_id: an order id
        status: new status of the order

    Returns:
        (Obj:) updated_order
    """

    def __init__(self, order_id, status):
        self.order_id = order_id
        self.status = status

    def change_status(self):
        update_order_status = Order.objects.filter(
            id=self.order_id).first()
        update_order_status.status = self.status
        update_order_status.save()


class SaveAutofillItems:
    def __init__(self, product_list, order_id):
        self.product_list = product_list
        self.order_id = order_id

    def save(self):
        if self.product_list:
            order_exists = AutoFillProducts.objects.filter(
                order_id=self.order_id)
            if not order_exists:
                for product in self.product_list:
                    AutoFillProducts.objects.get_or_create(
                        order_id=self.order_id,
                        product_unit_price=product.sales_price,
                        product_name=product.product_name,
                        sku_number=product.sku_number,
                        autofill_quantity=product.autofill_quantity,
                        preferred_supplier_id=product.preferred_supplier_id,
                        backup_supplier_id=product.backup_supplier_id,
                    )
            return AutoFillProducts.objects.filter(is_deleted=False)
        raise GraphQLError(
            "There are no data to be generated")
