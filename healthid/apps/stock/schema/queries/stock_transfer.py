from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.messages.stock_responses import STOCK_ERROR_RESPONSES
from healthid.utils.stock_utils.validate_stock_transfer import \
    validate
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.stock.schema.types import \
    StockTransferType
import graphene
from django.db.models import Q
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import StockTransfer


class StockTransferQuery(graphene.ObjectType):
    stock_transfers = graphene.List(StockTransferType)
    stock_transfer = graphene.Field(
        StockTransferType, transfer_number=graphene.String(required=True))

    @login_required
    def resolve_stock_transfers(self, info):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        stock_transfers = StockTransfer.objects.filter(
            Q(destination_outlet=outlet) | Q(sending_outlet=outlet))
        if not stock_transfers:
            raise GraphQLError(STOCK_ERROR_RESPONSES["zero_stock_transfers"])
        return stock_transfers

    @login_required
    def resolve_stock_transfer(self, info, **kwargs):
        """Method to retrieve a single stock transfer using its number
        """
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        validate.validate_transfer(kwargs['transfer_number'])
        stock_transfer = get_model_object(
            StockTransfer, 'id', kwargs['transfer_number'])
        sending_outlet = stock_transfer.sending_outlet
        destination_outlet = stock_transfer.destination_outlet

        if stock_transfer and (str(sending_outlet) == str(outlet)
                               or str(destination_outlet) == str(outlet)):
            return stock_transfer
        raise GraphQLError(STOCK_ERROR_RESPONSES["inexistent_stock_transfer"])
