from django.core.exceptions import ObjectDoesNotExist

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


class UpdateProposedProduct(graphene.Mutation):
    """
    update proposed product
    """
    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        product_category_id = graphene.Int()
        product_name = graphene.String()
        measurement_unit_id = graphene.Int()
        pack_size = graphene.String()
        sku_number = graphene.Int()
        description = graphene.String()
        brand = graphene.String()
        manufacturer = graphene.String()
        vat_status = graphene.String()
        quality = graphene.String()
        sales_price = graphene.Int()
        nearest_expiry_date = graphene.String()
        prefered_supplier_id = graphene.Int()
        backup_supplier_id = graphene.Int()
        tags = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        try:
            product = Product.objects.get(pk=id)
        except ObjectDoesNotExist:
            raise Exception(f"Product with an id of {id} does not exist")
        if product.is_approved:
            raise GraphQLError("Approved product can't be edited.")
        tags = kwargs.get("tags")
        kwargs.pop("tags")
        update_values = []
        for(key, value) in kwargs.items():
            if type(value) is str and value.strip() == "":
                raise GraphQLError(f"The {key} field can't be empty")
            if key is not None:
                handle_product_validations.handle_validation(**kwargs)
                if key == 'id':
                    continue
                update_values.append(key)
                setattr(product, key, value)
        product.save(update_fields=update_values)
        product.tags.set(*tags)
        message = 'Product successfully updated'
        return UpdateProposedProduct(
            product=product,
            message=message
        )


class DeleteProduct(graphene.Mutation):
    """
    Deletes product from database
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    def mutate(self, info, id):
        try:
            product = Product.objects.get(pk=id)
        except ObjectDoesNotExist:
            raise Exception(f"Product with an id of {id} does not exist")
        if product.is_approved:
            raise GraphQLError("Approved product can't be deleted.")
        product.delete()

        return DeleteProduct(
            success="Product has been deleted"
        )


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_proposed_product = UpdateProposedProduct.Field()
    delete_product = DeleteProduct.Field()
