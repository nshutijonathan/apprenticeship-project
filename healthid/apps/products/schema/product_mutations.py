from django.core.exceptions import ObjectDoesNotExist

import graphene
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import BatchInfo, Product
from healthid.apps.products.schema.product_query import BatchInfoType
from healthid.utils.auth_utils.decorator import admin_required
from healthid.utils.product_utils import handle_product_validations
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.utils.product_utils.product_querysets import ProductModelQuery

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
        prefered_supplier_id = graphene.String()
        backup_supplier_id = graphene.String()
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


class CreateBatchInfo(graphene.Mutation):
    """
        Mutation to create a Product batch Information
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        supplier_id = graphene.String(required=True)
        product = graphene.List(graphene.Int, required=True)
        date_received = graphene.String()
        pack_size = graphene.String()
        quantity_received = graphene.Int(required=True)
        expiry_date = graphene.String()
        unit_cost = graphene.Float(required=True)
        commentary = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @batch_info_instance
    def mutate(self, info, **kwargs):
        supplier_id = kwargs.get('supplier_id')
        products = kwargs.get('product')
        supplier_instance = \
            ProductModelQuery().query_supplier_id(supplier_id)
        batch_info = BatchInfo.objects.create(
            date_received=parse_date(kwargs.get('date_received')),
            pack_size=kwargs.get('pack_size'),
            quantity_received=kwargs.get('quantity_received'),
            expiry_date=parse_date(kwargs.get('expiry_date')),
            unit_cost=kwargs.get('unit_cost'),
            commentary=kwargs.get('commentary'),
            supplier=supplier_instance
        )
        for product in products:
            product_instance = \
                ProductModelQuery().query_product_id(product)
            batch_info.product.add(product_instance)
        batch_info.save()
        message = [f'Batch successfully created']
        return CreateBatchInfo(message=message, batch_info=batch_info)


class UpdateBatchInfo(graphene.Mutation):
    """
        Mutation to update a Product batch Information
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        batch_id = graphene.String(required=True)
        supplier_id = graphene.String()
        product = graphene.List(graphene.Int)
        date_received = graphene.String()
        pack_size = graphene.String()
        quantity_received = graphene.Int()
        expiry_date = graphene.String()
        unit_cost = graphene.Float()
        commentary = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @batch_info_instance
    @admin_required
    def mutate(self, info, **kwargs):
        batch_id = kwargs.get('batch_id')
        update_values = []
        batch_info = ProductModelQuery().query_batch_info(batch_id)
        if kwargs.get('product'):
            products = kwargs.get('product')
            batch_info.product.clear()
            for product in products:
                product_instance = \
                    ProductModelQuery().query_product_id(product)
                batch_info.product.add(product_instance)
        if kwargs.get('supplier_id'):
            supplier_id = kwargs.get('supplier_id')
            supplier_instance = \
                ProductModelQuery().query_supplier_id(supplier_id)
            batch_info.supplier = supplier_instance
            update_values.append('supplier')
        for (key, value) in kwargs.items():
            if key is not None:
                if key == 'batch_id' or \
                        key == 'supplier_id' \
                        or key == 'product':
                    continue
                if key == 'date_received' or \
                        key == 'expiry_date':
                    update_values.append(key)
                    setattr(batch_info, key, parse_date(value))
                    continue
                update_values.append(key)
                setattr(batch_info, key, value)
        batch_info.save(update_fields=update_values)
        message = [f'Batch with number {batch_info.batch_no} '
                   f'successfully updated']
        return UpdateBatchInfo(message=message, batch_info=batch_info)


class DeleteBatchInfo(graphene.Mutation):
    """
        Delete a Product batch Info Mutation
    """

    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        batch_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    @admin_required
    def mutate(root, info, **kwargs):
        batch_id = kwargs.get('batch_id')
        batch_info = ProductModelQuery().query_batch_info(batch_id)
        batch_info.delete()
        message = [f"Batch with number {batch_info.batch_no} has been deleted"]
        return DeleteBatchInfo(message=message)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_proposed_product = UpdateProposedProduct.Field()
    delete_product = DeleteProduct.Field()
    create_batch_info = CreateBatchInfo.Field()
    update_batch_info = UpdateBatchInfo.Field()
    delete_batch_info = DeleteBatchInfo.Field()
