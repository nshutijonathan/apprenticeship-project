import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.orders.models.orders import SupplierOrderDetails, Order
from healthid.utils.app_utils.database import SaveContextManager
from healthid.utils.app_utils.database import get_model_object


class CancelOrder(graphene.Mutation):
    """Cancel single/multiple supplier order(s) or cancel single/multiple initiated order(s)

    Args:
        supplier_order_ids: A list of supplier order ids
        order_ids: A list of initiated order ids

    Returns:
        message: a return message.
    """
    message = graphene.String()

    class Arguments:
        order_ids = graphene.List(graphene.Int)
        supplier_order_ids = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        order_ids = kwargs.get('order_ids')
        supplier_order_ids = kwargs.get('supplier_order_ids')

        if supplier_order_ids:
            for supplier_order in supplier_order_ids:
                removed_order = get_model_object(
                    SupplierOrderDetails,
                    'id',
                    supplier_order
                )
                if removed_order:
                    removed_order.hard_delete()

        if order_ids:
            for order_id in order_ids:
                removed_initiated_order = get_model_object(
                    Order,
                    'id',
                    order_id
                )
                if removed_initiated_order:
                    removed_initiated_order.hard_delete()
        if not order_ids and not supplier_order_ids:
            return CancelOrder(message="Provide the order to be placed")

        return CancelOrder(message="Order(s) cancelled successfully")
