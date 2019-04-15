import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.products.models import Product
from healthid.utils.product_utils import handle_product_validations

from .product_query import ProductType


class ProductInput(graphene.InputObjectType):
    """
        Specifying the data types of the product Input
    """
    Product = graphene.String()


class CreateProduct(graphene.Mutation):
    """
        Mutation to create a product.
    """
    product = graphene.Field(ProductType)

    class Arguments:
        product_category_id = graphene.Int()
        product_name = graphene.String(required=True)
        measurement_unit_id = graphene.Int(required=True)
        pack_size = graphene.String()
        sku_number = graphene.Int()
        description = graphene.String(required=True)
        brand = graphene.String(required=True)
        manufacturer = graphene.String(required=True)
        vat_status = graphene.String(required=True)
        quality = graphene.String(required=True)
        sales_price = graphene.Int(required=True)
        nearest_expiry_date = graphene.String()
        prefered_supplier_id = graphene.Int()
        backup_supplier_id = graphene.Int()
        tags = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        product = Product()
        tags = kwargs.get("tags")
        kwargs.pop("tags")
        for (key, value) in kwargs.items():
            if type(value) is str and value.strip() == "":
                raise GraphQLError("The {} field can't be empty".format(key))
            handle_product_validations.handle_validation(**kwargs)
            setattr(product, key, value)
        product.save()
        for tag in tags:
            product.tags.add(tag)
        return CreateProduct(product=product)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
