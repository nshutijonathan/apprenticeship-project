"""Service objects that implement business logic."""

from healthid.apps.orders.models import Order, SupplierOrderDetails
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.app_utils.database import (get_model_object,
                                               SaveContextManager)
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES


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

        Get all supplieer order details belong to provided order and match
        the provided ids.

        Returns:
            (Obj:) QuerySet object of supplier order details
        """
        order = get_model_object(Order, 'id', self.order_id)
        results = SupplierOrderDetails.objects.all()
        results = results.filter(id__in=self.supplier_order_details_ids,
                                 order=order)
        results = results.select_related('supplier')

        if not results:
            raise ValueError("No supplier Order Details found matching"
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
            email = detail.supplier.email
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
                supplier_order.additional_notes = self.addtional_notes

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
