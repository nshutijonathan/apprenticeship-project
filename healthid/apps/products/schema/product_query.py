from datetime import datetime

import graphene
from django.core.exceptions import ValidationError
from graphene.utils.resolve_only_args import resolve_only_args
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.products.models import (BatchInfo, MeasurementUnit, Product,
                                           ProductCategory)
from taggit.managers import TaggableManager
from healthid.utils.app_utils.database import get_model_object


@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return graphene.List(graphene.String, source='get_tags')


class BatchInfoType(DjangoObjectType):
    class Meta:
        model = BatchInfo


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory


class MeasurementUnitType(DjangoObjectType):
    class Meta:
        model = MeasurementUnit


class ProductType(DjangoObjectType):
    product_quantity = graphene.Int()

    class Meta:
        model = Product
        filter_fields = {
            'is_approved': ['exact'],
            'product_name': ['exact', 'icontains', 'istartswith'],
            'sku_number': ['exact'],
            'tags__name': ['exact', 'icontains', 'istartswith']
        }
        interfaces = (graphene.relay.Node, )

    def resolve_product_quantity(self, info, **kwargs):
        if self is not None:
            product = Product.objects.get(product_name=self)
            product_batches = product.batch_info.all()
            quantities = []
            for product_batch in product_batches:
                quantities.append(int(product_batch.quantity_received))
            product_quantity = sum(quantities)
            return product_quantity

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class Query(graphene.AbstractType):
    products = graphene.List(ProductType)
    proposed_products = graphene.List(ProductType)
    all_batch_info = graphene.List(BatchInfoType)
    batch_info = graphene.Field(
        BatchInfoType, id=graphene.String(required=True))
    product_batch_info = graphene.List(
        BatchInfoType, id=graphene.Int(required=True))
    approved_products = graphene.List(ProductType)
    filter_products = DjangoFilterConnectionField(ProductType)
    proposed_edits = graphene.List(ProductType)

    product = graphene.Field(
        ProductType,
        id=graphene.Int(),
        product_name=graphene.String(),
        pack_size=graphene.String(),
        sku_number=graphene.Int(),
        description=graphene.String(),
        brand=graphene.String(),
        manufacturer=graphene.String(),
        quality=graphene.String(),
        sales_price=graphene.Int(),
        nearest_expiry_date=graphene.String(),
        tags=graphene.List(graphene.String))

    batch_expiries = graphene.Field(
        product_batch_info,
        start_date=graphene.String(),
        end_date=graphene.String(required=True)
    )
    expired_batches = graphene.Field(
        product_batch_info
    )
    deactivated_products = graphene.List(ProductType)
    product_categories = graphene.List(ProductCategoryType)
    measurement_unit = graphene.List(MeasurementUnitType)

    @login_required
    def resolve_products(self, info):
        all_products = Product.objects.all()
        return all_products

    @login_required
    def resolve_filter_products(self, info, **kwargs):

        for key in kwargs:
            if isinstance(kwargs[key], str) and kwargs[key].strip() == "":
                raise GraphQLError('Please provide a valid search keyword')

        response = Product.objects.filter(**kwargs).order_by("product_name")
        if not response:
            raise GraphQLError("Product matching '{}' does not exist".format(
                kwargs[key].strip()))
        return response

    @login_required
    def resolve_approved_products(self, info):
        return Product.objects.filter(is_approved=True)

    @login_required
    def resolve_product(self, info, **kwargs):
        id = kwargs.get('id')
        if id:
            return get_model_object(Product, 'id', id)
        raise GraphQLError("Please provide the product id")

    @login_required
    def resolve_proposed_edits(self, info):
        return Product.objects.exclude(parent_id__isnull=True)

    @login_required
    def resolve_product_categories(self, info):
        return ProductCategory.objects.all()

    @login_required
    def resolve_measurement_unit(self, info):
        return MeasurementUnit.objects.all()


class BatchQuery(graphene.AbstractType):
    all_batch_info = graphene.List(BatchInfoType)
    batch_info = graphene.Field(
        BatchInfoType, id=graphene.String(required=True))
    product_batch_info = graphene.List(
        BatchInfoType, id=graphene.Int(required=True))

    @login_required
    def resolve_all_batch_info(self, info):
        return BatchInfo.objects.all()

    @login_required
    def resolve_batch_info(self, info, **kwargs):
        return get_model_object(BatchInfo, 'id', kwargs.get('id'))

    @login_required
    def resolve_product_batch_info(self, info, **kwargs):
        product = get_model_object(Product, 'id', kwargs.get('id'))
        product_batches = product.batch_info.all()
        return product_batches

    @login_required
    def resolve_batch_expiries(self, info, **kwargs):

        start_date = kwargs.get("start_date") or datetime.now()
        end_date = kwargs.get("end_date")
        try:
            return BatchInfo.objects.filter(
                expiry_date__range=(start_date, end_date))
        except ValidationError as e:
            raise GraphQLError("The {}".format(e.messages[0]))

    @login_required
    def resolve_expired_batches(self, info, **kwargs):
        start_date = datetime.now()
        return BatchInfo.objects.filter(expiry_date__lt=start_date)

    @login_required
    @user_permission('Operations Admin')
    def resolve_deactivated_products(self, info, **kwargs):
        return Product.all_products.filter(is_active=False)
