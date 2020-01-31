import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import SupplierOrderDetails, Order
from healthid.utils.app_utils.database import SaveContextManager
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES
from healthid.apps.orders.services import SupplierOrderDetailsFetcher, OrderStatusChangeService


class MarkSupplierOrderAsSent(graphene.Mutation):
    """Mark Supplier Order Details as sent

    Mark BooleanField marked_as_sent

    Args:
        supplier_order_ids: A list of supplier order ids

    Returns:
        message: a return message.
    """
    message = graphene.String()

    class Arguments:
        supplier_order_ids = graphene.List(graphene.String,
                                           required=True)

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_ids = kwargs.get('supplier_order_ids')
        details_fetcher = SupplierOrderDetailsFetcher(supplier_order_ids)
        supplier_orders = details_fetcher.fetch()
        ids = list()
        for supplier_order in supplier_orders:
            supplier_order.marked_as_sent = True
            supplier_order.status = "open"
            ids.append(supplier_order.id)
            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                pass
        message = ORDERS_SUCCESS_RESPONSES[
            "supplier_order_marked_closed"].format(
                ",".join(id for id in ids))
        return MarkSupplierOrderAsSent(message=message)
