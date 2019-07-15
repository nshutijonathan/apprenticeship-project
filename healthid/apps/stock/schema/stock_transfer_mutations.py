import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.apps.stock.models import StockTransfer, StockTransferRecord
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import (
    check_validity_of_ids, check_validity_of_quantity)
from healthid.utils.stock_utils.validate_stock_transfer import validate
from healthid.utils.messages.stock_responses import\
      STOCK_ERROR_RESPONSES, STOCK_SUCCESS_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet


class StockTransferType(DjangoObjectType):
    class Meta:
        model = StockTransfer


class OpenStockTransfer(graphene.Mutation):
    """Mutation to open a stock transfer
    """

    stock_transfer = graphene.Field(StockTransferType)
    success = graphene.List(graphene.String)

    class Arguments:
        batch_ids = graphene.List(graphene.String, required=True)
        product_id = graphene.Int(required=True)
        quantities = graphene.List(graphene.Int, required=True)
        destination_outlet_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        user = info.context.user

        validate.validate_fields(**kwargs)
        product_id = kwargs['product_id']
        batch_ids = kwargs['batch_ids']
        quantities = kwargs['quantities']

        product = get_model_object(Product, 'id', product_id)
        sending_outlet = check_user_has_an_active_outlet(user)
        destination_outlet = get_model_object(
            Outlet, 'id', kwargs['destination_outlet_id'])
        if str(sending_outlet) == str(destination_outlet):
            raise GraphQLError(
                STOCK_ERROR_RESPONSES["outlet_transfer_validation"])
        product_batch_ids = product.batch_info.values_list("id", flat=True)

        message = "Batch with ids {} do not exist in this product"
        check_validity_of_ids(batch_ids, product_batch_ids, message=message)
        product_batch_quantities = [product.batch_info.get(
            id=id).quantity for id in batch_ids]

        check_validity_of_quantity(
            quantities, product_batch_quantities, batch_ids)

        stock_transfer = StockTransfer(
            product=product,
            sending_outlet=sending_outlet,
            destination_outlet=destination_outlet
        )

        with SaveContextManager(stock_transfer) as stock_transfer:
            for index, value in enumerate(batch_ids):
                stock_transfer_record = StockTransferRecord.objects.create(
                    quantity=quantities[index],
                    batch_id=value
                )
                stock_transfer.stock_transfer_record.add(stock_transfer_record)

        success = [STOCK_SUCCESS_RESPONSES["stock_transfer_open_success"]]
        return OpenStockTransfer(
            stock_transfer=stock_transfer, success=success)


class CloseStockTransfer(graphene.Mutation):
    """Mutation to mark a transfer as complete
    """

    success = graphene.Field(graphene.String)

    class Arguments:
        transfer_number = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        destination_outlet = check_user_has_an_active_outlet(user)
        transfer = StockTransfer.objects.filter(
            id=kwargs['transfer_number'],
            destination_outlet=destination_outlet).first()
        if not transfer:
            raise GraphQLError(STOCK_ERROR_RESPONSES["close_transfer_error"])
        transfer.complete_status = False
        transfer.save()

        success = STOCK_SUCCESS_RESPONSES["stock_transfer_close_success"]
        return CloseStockTransfer(success=success)
