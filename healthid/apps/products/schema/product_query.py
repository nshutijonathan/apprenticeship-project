import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from taggit.managers import TaggableManager

from healthid.apps.products.models import BatchInfo, Product


@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return graphene.List(graphene.String, source='get_tags')


class BatchInfoType(DjangoObjectType):

    class Meta:
        model = BatchInfo


class ProductType(DjangoObjectType):
    product_quantity = graphene.Int()

    class Meta:
        model = Product

    def resolve_product_quantity(self, info, **kwargs):
        if self is not None:
            product = Product.objects.get(product_name=self)
            product_batches = product.batch_info.all()
            quantities = []
            for product_batch in product_batches:
                quantities.append(int(product_batch.quantity_received))
            product_quantity = sum(quantities)
            return product_quantity


class Query(graphene.AbstractType):

    products = graphene.List(ProductType)
    proposed_products = graphene.List(ProductType)
    all_batch_info = graphene.List(BatchInfoType)
    batch_info = graphene.Field(
        BatchInfoType,
        id=graphene.String(required=True))
    product_batch_info = graphene.List(
        BatchInfoType,
        id=graphene.Int(required=True)
    )
    approved_products = graphene.List(ProductType)

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

    @login_required
    def resolve_products(self, info):
        all_products = Product.objects.all()
        return all_products

    @login_required
    def resolve_approved_products(self, info):
        return Product.objects.filter(is_approved=True)

    @login_required
    def resolve_product(self, info, **kwargs):
        id = kwargs.get('id')
        try:
            if id:
                return Product.objects.get(pk=id)
            raise GraphQLError("Please provide the product id")
        except ObjectDoesNotExist:
            raise GraphQLError("Product with Id {} doesn't exist".format(id))

    @login_required
    def resolve_proposed_products(self, info):
        return Product.objects.filter(is_approved=False)

    @login_required
    def resolve_all_batch_info(self, info):
        return BatchInfo.objects.all()

    @login_required
    def resolve_batch_info(self, info, **kwargs):
        batch_info_id = kwargs.get('id')
        try:
            if batch_info_id is not None:
                return BatchInfo.objects.get(id=batch_info_id)
        except ObjectDoesNotExist:
            raise GraphQLError(
                "Batch Info with Id {} doesn't "
                "exist".format(batch_info_id)
            )

    @login_required
    def resolve_product_batch_info(self, info, **kwargs):
        product_id = kwargs.get('id')
        try:
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                product_batches = product.batch_info.all()
                return product_batches
        except ObjectDoesNotExist:
            raise GraphQLError(
                "Product with Id {} doesn't "
                "exist".format(product_id)
            )
