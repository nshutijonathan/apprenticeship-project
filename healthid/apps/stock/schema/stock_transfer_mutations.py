import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import BatchInfo
from healthid.apps.stock.models import StockTransfer, StockTransferRecord
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import (
    check_validity_of_ids, check_validity_of_quantity)
from healthid.utils.stock_utils.validate_stock_transfer import validate
from healthid.utils.messages.stock_responses import\
      STOCK_ERROR_RESPONSES, STOCK_SUCCESS_RESPONSES


class StockTransferType(DjangoObjectType):
    class Meta:
        model = StockTransfer


class OpenStockTransfer(graphene.Mutation):
    """Mutation to open a stock transfer
    """

    stock_transfer = graphene.Field(StockTransferType)
    success = graphene.List(graphene.String)

    class Arguments:
        batch_number = graphene.String(required=True)
        products = graphene.List(graphene.Int, required=True)
        quantities = graphene.List(graphene.Int, required=True)
        destination_outlet_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        user = info.context.user

        validate.validate_fields(**kwargs)
        products = kwargs['products']
        quantities = kwargs['quantities']

        batch = get_model_object(BatchInfo, 'batch_no', kwargs['batch_number'])
        sending_outlet = get_model_object(Outlet, 'user', user)
        destination_outlet = get_model_object(
            Outlet, 'id', kwargs['destination_outlet_id'])
        if str(sending_outlet) == str(destination_outlet):
            raise GraphQLError(
                  STOCK_ERROR_RESPONSES["outlet_transfer_validation"])
        batch_product_ids = batch.product.values_list("id", flat=True)

        check_validity_of_ids(kwargs['products'], batch_product_ids)
        batch_product_quantities = [batch.batch_quantities.get(
            product_id=id).quantity_received for id in products]
        check_validity_of_quantity(
            quantities, batch_product_quantities, products)

        stock_transfer = StockTransfer(
            batch=batch,
            sending_outlet=sending_outlet,
            destination_outlet=destination_outlet
        )

        with SaveContextManager(stock_transfer) as stock_transfer:
            for index, value in enumerate(products):
                stock_transfer_record = StockTransferRecord.objects.create(
                    quantity=quantities[index],
                    product_id=value
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

        destination_outlet = get_model_object(Outlet, 'user', user)
        transfer = StockTransfer.objects.filter(
            id=kwargs['transfer_number'],
            destination_outlet=destination_outlet).first()
        if not transfer:
            raise GraphQLError(STOCK_ERROR_RESPONSES["close_transfer_error"])
        transfer.complete_status = False
        transfer.save()

        success = STOCK_SUCCESS_RESPONSES["stock_transfer_close_success"]
        return CloseStockTransfer(success=success)
