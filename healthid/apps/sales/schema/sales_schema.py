import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.sales.models import (SalesPrompt, Sale)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission


class SalesPromptType(DjangoObjectType):
    class Meta:
        model = SalesPrompt


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
