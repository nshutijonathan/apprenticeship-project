import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from django.forms import model_to_dict
from healthid.apps.products.models import ProductCategory
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_belongs_to_outlet

from .product_query import ProductCategoryType


class CreateProductCategory(graphene.Mutation):
    """
        Mutation to create a Product Category
    """
    product_category = graphene.Field(ProductCategoryType)

    class Arguments:
        name = graphene.String(required=True)
        outlet_id = graphene.Int(required=True)
        loyalty_weight = graphene.Int()
        amount_paid = graphene.Int()
        markup = graphene.Int(required=True)
        is_vat_applicable = graphene.Boolean(required=True)

    message = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError("Product category name cannot be blank")
        check_user_belongs_to_outlet(info.context.user,
                                     kwargs.get('outlet_id'))
        product_category = ProductCategory(**kwargs)
        with SaveContextManager(product_category, model=ProductCategory):
            message = ['Product Category created successfully']
            return CreateProductCategory(
                message=message, product_category=product_category)


class EditProductCategory(graphene.Mutation):
    """
    Mutation to edit a Product Category
    """
    product_category = graphene.Field(ProductCategoryType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        loyalty_weight = graphene.Int()
        amount_paid = graphene.Int()
        markup = graphene.Int()
        is_vat_applicable = graphene.Boolean()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError("This name field can't be empty")
        product_category = get_model_object(ProductCategory, 'id', id)
        check_user_belongs_to_outlet(info.context.user,
                                     product_category.outlet.id)
        # add fields with changed values to new dictionary
        changed_fields = {
            key: kwargs.get(key)
            for key, value in model_to_dict(product_category).items()
            if key in kwargs and value != kwargs.get(key)}
        if not changed_fields:
            return EditProductCategory(
                message="Product category unchanged, nothing to edit.",
                product_category=product_category)
        for field, value in changed_fields.items():
            setattr(product_category, field, value)
        with SaveContextManager(product_category, model=ProductCategory):
            return EditProductCategory(
                message='Product Category successfully updated',
                product_category=product_category)


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
        user = info.context.user
        product_category = get_model_object(ProductCategory, 'id', id)
        check_user_belongs_to_outlet(info.context.user,
                                     product_category.outlet.id)
        product_category.delete(user)
        message = f'Prduct category of Id {id} has been successfully deleted'

        return DeleteProductCategory(message=message)
