import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import SupplierOrderDetails
from healthid.utils.app_utils.database import SaveContextManager
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES
from healthid.apps.orders.services import SupplierOrderDetailsFetcher, OrderStatusChangeService


class AddOrderNotes(graphene.Mutation):
    """
    Add a note to the supplier order form

    Args:
        supplier_order_id: A supplier order id

    Returns:
        message: a return message.
    """
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_id = graphene.String(required=True)
        additional_notes = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        additional_notes = kwargs.get('additional_notes')
        supplier_order_id = kwargs.get('supplier_order_id')
        supplier_order = SupplierOrderDetails.objects.filter(
            order_id=order_id, id=supplier_order_id).first()
        if supplier_order and additional_notes:
            supplier_order.additional_notes = additional_notes
            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                pass
            message = ORDERS_SUCCESS_RESPONSES[
                "add_order_note_success"]
            return AddOrderNotes(message=message)
        return AddOrderNotes(message="Order Id or additional notes cannot be empty")
