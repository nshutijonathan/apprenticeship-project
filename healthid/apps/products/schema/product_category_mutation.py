import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.products.models import ProductCategory
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission

from .product_query import ProductCategoryType


class CreateProductCategory(graphene.Mutation):
    """
        Mutation to create a Product Category
    """
    product_category = graphene.Field(ProductCategoryType)

    class Arguments:
        name = graphene.String(required=True)

    message = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError("This name field can't be empty")
        params = {'model_name': 'ProductCategory', 'value': name}
        product_category = ProductCategory(name=name)
        with SaveContextManager(product_category, **params):
            message = [f'Product Category created succesfully']
            return CreateProductCategory(
                message=message, product_category=product_category)


class EditProductCategory(graphene.Mutation):
    """
    update productcategory
    """
    product_category = graphene.Field(ProductCategoryType)
    message = graphene.String()

    class Arguments:
        name = graphene.String()
        id = graphene.Int()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError("This name field can't be empty")
        product_category = get_model_object(ProductCategory, 'id', id)
        product_category.name = name
        params = {'model_name': 'ProductCategory', 'value': name}
        with SaveContextManager(product_category, **params):
            message = 'Product category successfully updated'
            return EditProductCategory(
                message=message, product_category=product_category)


class DeleteProductCategory(graphene.Mutation):
    """
        Delete a product category
    """
    product_category = graphene.Field(ProductCategoryType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        product_category = get_model_object(ProductCategory, 'id', id)
        product_category.delete()
        message = f'Prduct category of Id {id} has been successfully deleted'

        return DeleteProductCategory(message=message)
