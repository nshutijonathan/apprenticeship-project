import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene import List, String
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.products.models import Product
from taggit.managers import TaggableManager


@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return List(String, source='get_tags')


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class Query(graphene.AbstractType):

    products = graphene.List(ProductType)

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
        return Product.objects.all()

    @login_required
    def resolve_product(self, info, **kwargs):
        id = kwargs.get('id')
        try:
            if id:
                return Product.objects.get(pk=id)
            raise GraphQLError("Please provide the product id")
        except ObjectDoesNotExist:
            raise GraphQLError("Product with Id {} doesn't exist".format(id))
