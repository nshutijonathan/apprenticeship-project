import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import (StockCount, StockCountTemplate,
                                        StockTransfer)
from healthid.apps.stock.schema.stock_transfer_mutations import \
    StockTransferType
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.stock_utils.validate_stock_transfer import \
    validate
from healthid.utils.messages.stock_responses import STOCK_ERROR_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet


class StockCountTemplateType(DjangoObjectType):
    class Meta:
        model = StockCountTemplate


class StockTemplateQuery(graphene.ObjectType):
    stock_templates = graphene.List(
        StockCountTemplateType,
        outlet_id=graphene.Int(required=True))
    stock_template = graphene.Field(
        StockCountTemplateType,
        template_id=graphene.Int(required=True),
        outlet_id=graphene.Int(required=True)
    )

    @login_required
    def resolve_stock_templates(self, info, **kwargs):
        outlet_id = kwargs.get('outlet_id')
        return StockCountTemplate.objects.filter(outlet_id=outlet_id)

    @login_required
    def resolve_stock_template(self, info, **kwargs):
        template_id = kwargs.get('template_id')
        outlet_id = kwargs.get('outlet_id')
        return StockCountTemplate.objects.filter(
            outlet_id=outlet_id, id=template_id).first()


class StockCountType(DjangoObjectType):
    class Meta:
        model = StockCount


class StockCountQuery(graphene.AbstractType):
    stock_counts = graphene.List(StockCountType)
    stock_count = graphene.Field(
        StockCountType,
        id=graphene.String(required=True))
    approved_stock_counts = graphene.List(StockCountType)
    unresolved_stock_counts = graphene.List(StockCountType)

    @login_required
    def resolve_stock_counts(self, info):
        all_stock_counts = StockCount.objects.all()
        return all_stock_counts

    @login_required
    def resolve_stock_count(self, info, **kwargs):
        stock_count_id = kwargs.get('id')
        return get_model_object(StockCount, 'id', stock_count_id)

    @login_required
    @user_permission("Manager")
    def resolve_approved_stock_counts(self, info):
        ''' This method queries all approved stock counts

            Returns:
                  it returns a list of approved stock counts
        '''
        return StockCount.objects.filter(is_approved=True)

    @login_required
    @user_permission("Manager")
    def resolve_unresolved_stock_counts(self, info):
        ''' This method queries all unresolved stock counts.

            returns:
               it returns a list of unresolved stock counts
        '''
        return StockCount.objects.filter(is_approved=False)


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


class Query(
    StockTemplateQuery,
    StockCountQuery,
    StockTransferQuery,
    graphene.ObjectType


):
    pass
