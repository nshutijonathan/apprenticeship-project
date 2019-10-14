import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order
from healthid.utils.app_utils.database import get_model_object


class CloseOrder(graphene.Mutation):
    """
    Mutation to initiate an order in the database

     arguments:
         order_id(int): name of the order to initiate

     returns:
        message(str): message containing operation response
    """
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, order_id):
        order = get_model_object(Order, 'id', order_id)
        message = order.close(info.context.user)
        return CloseOrder(message=message)
