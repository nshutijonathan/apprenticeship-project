import graphene
from graphene_django import DjangoObjectType
from graphene.utils.resolve_only_args import resolve_only_args
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.sales.models import (
    Sale, SaleDetail, SalesPrompt, SaleReturn, SaleReturnDetail)

from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES


class SalesPromptType(DjangoObjectType):
    class Meta:
        model = SalesPrompt


class SaleDetailType(DjangoObjectType):
    class Meta:
        model = SaleDetail


class SaleType(DjangoObjectType):
    register_id = graphene.Int(source='get_default_register')

    class Meta:
        model = Sale
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class ConsultationPaymentType(DjangoObjectType):

    class Meta:
        model = Sale


class SaleReturnType(DjangoObjectType):

    class Meta:
        model = SaleReturn


class SaleReturnDetailType(DjangoObjectType):
    class Meta:
        model = SaleReturnDetail


class Query(graphene.ObjectType):
    """
    Return a list of sales prompt.
    Or return a single sales prompt specified.
    """

    sales_prompts = graphene.List(SalesPromptType)
    sales_prompt = graphene.Field(SalesPromptType, id=graphene.Int())

    outlet_sales_history = graphene.List(SaleType,
                                         outlet_id=graphene.Int(required=True),
                                         search=graphene.String(),
                                         page_count=graphene.Int(),
                                         page_number=graphene.Int())
    all_sales_history = graphene.List(SaleType,
                                      page_count=graphene.Int(),
                                      page_number=graphene.Int())

    sale_history = graphene.Field(
        SaleType, sale_id=graphene.Int(required=True))

    @login_required
    @user_permission('Manager')
    def resolve_sales_prompts(self, info, **kwargs):
        return SalesPrompt.objects.all()

    @login_required
    @user_permission('Manager')
    def resolve_sales_prompt(self, info, **kwargs):
        id = kwargs.get('id')
        sales_prompt = get_model_object(SalesPrompt, 'id', id)
        return sales_prompt

    @login_required
    def resolve_outlet_sales_history(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        search = kwargs.get('search')
        outlet_id = kwargs.get('outlet_id')

        sale = Sale()
        resolved_value = sale.sales_history(
            outlet_id=outlet_id, search=search)

        if page_count or page_number:
            sales = pagination_query(
                resolved_value, page_count, page_number)
            Query.pagination_result = sales
            return sales[0]
        if resolved_value:
            paginated_response = pagination_query(resolved_value,
                                                  PAGINATION_DEFAULT[
                                                      "page_count"],
                                                  PAGINATION_DEFAULT[
                                                      "page_number"])

            Query.pagination_result = paginated_response
            return paginated_response[0]
        return GraphQLError(SALES_ERROR_RESPONSES["no_sales_error"])

    @login_required
    def resolve_sale_history(self, info, sale_id):
        sale = get_model_object(Sale, 'id', sale_id)
        return sale

    @login_required
    @user_permission('Manager')
    def resolve_all_sales_history(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')

        resolved_value = Sale.objects.all()

        if page_count or page_number:
            sales = pagination_query(
                resolved_value, page_count, page_number)
            Query.pagination_result = sales
            return sales[0]
        if resolved_value:
            paginated_response = pagination_query(resolved_value,
                                                  PAGINATION_DEFAULT[
                                                      "page_count"],
                                                  PAGINATION_DEFAULT[
                                                      "page_number"])

            Query.pagination_result = paginated_response
            return paginated_response[0]
        return GraphQLError(SALES_ERROR_RESPONSES["no_sales_error"])
