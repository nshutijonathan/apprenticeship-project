import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.sales.models import (Sale, SaleDetail, SalesPrompt)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission


class SalesPromptType(DjangoObjectType):
    class Meta:
        model = SalesPrompt


class SaleDetailType(DjangoObjectType):
    class Meta:
        model = SaleDetail


class SaleType(DjangoObjectType):
    class Meta:
        model = Sale


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
                                         first=graphene.Int(),
                                         skip=graphene.Int())

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
    def resolve_outlet_sales_history(self, info, outlet_id, search=None,
                                     first=None, skip=None):
        sale = Sale()
        sales = sale.sales_history(
            outlet_id=outlet_id, search=search, first=first, skip=skip)
        return sales

    @login_required
    def resolve_sale_history(self, info, sale_id):
        sale = get_model_object(Sale, 'id', sale_id)
        return sale
