import graphene
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import BatchInfo, Product, ProductCategory
from healthid.apps.products.schema.product_query import BatchInfoType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import (
    admin_or_manager_required, admin_required,
    operations_or_master_admin_required)
from healthid.utils.product_utils import handle_product_validations
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.utils.product_utils.product_query import ProductQuery
from healthid.utils.product_utils.set_price import SetPrice

from .product_query import ProductCategoryType, ProductType


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
        sales_price = graphene.Float()
        nearest_expiry_date = graphene.String()
        prefered_supplier_id = graphene.Int()
        backup_supplier_id = graphene.Int()
        tags = graphene.List(graphene.String)
        unit_cost = graphene.Float()

    @login_required
    def mutate(self, info, **kwargs):
        product = Product()
        tags = kwargs.get("tags")
        kwargs.pop("tags")
        for (key, value) in kwargs.items():
            if type(value) is str and value.strip() == "":
                raise GraphQLError("The {} field can't be empty".format(key))
            handle_product_validations.handle_validation(**kwargs)
            if key == 'product_name':
                params = {'model_name': 'Product',
                          'field': 'product_name', 'value': value}
            setattr(product, key, value)
        with SaveContextManager(product, **params):
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
        product = get_model_object(Product, 'id', id)
        handle_product_validations.handle_validation(**kwargs)
        if product.is_approved:
            raise GraphQLError("Approved product can't be edited.")
        tags = kwargs.get("tags")
        kwargs.pop("tags")
        for(key, value) in kwargs.items():
            if key == 'id':
                continue
            if type(value) is str and value.strip() == "":
                raise GraphQLError(f"The {key} field can't be empty")
            setattr(product, key, value)
        params = {'model_name': 'Product',
                  'field': 'product_name', 'value': product.product_name}
        with SaveContextManager(product, **params):
            product.tags.set(*tags)
            message = 'Product successfully updated'
            return UpdateProposedProduct(product=product, message=message)


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
        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            raise GraphQLError("Approved product can't be deleted.")
        product.delete()

        return DeleteProduct(success="Product has been deleted")


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
        supplier_instance = get_model_object(
            Suppliers, 'supplier_id', supplier_id)
        batch_info = BatchInfo.objects.create(
            date_received=parse_date(kwargs.get('date_received')),
            pack_size=kwargs.get('pack_size'),
            quantity_received=kwargs.get('quantity_received'),
            expiry_date=parse_date(kwargs.get('expiry_date')),
            unit_cost=kwargs.get('unit_cost'),
            commentary=kwargs.get('commentary'),
            supplier=supplier_instance
        )
        for product_id in products:
            product_instance = get_model_object(Product, 'id', product_id)
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
        products = kwargs.get('product')
        supplier_id = kwargs.get('supplier_id')
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        if products:
            batch_info.product.clear()
            for product_id in products:
                product_instance = get_model_object(Product, 'id', product_id)
                batch_info.product.add(product_instance)
        if supplier_id:
            supplier_instance = get_model_object(
                Suppliers, 'supplier_id', supplier_id)
            batch_info.supplier = supplier_instance
        for (key, value) in kwargs.items():
            if key is not None:
                if key in ('batch_id', 'supplier_id', 'product'):
                    continue
                if key in ('date_received', 'expiry_date'):
                    value = parse_date(value)
                setattr(batch_info, key, value)
        batch_info.save()
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
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        batch_info.delete()
        message = [f"Batch with number {batch_info.batch_no} has been deleted"]
        return DeleteBatchInfo(message=message)


class ApproveProduct(graphene.Mutation):
    """
      Mutation to approve proposed products a product.
    """

    class Arguments:
        product_id = graphene.Int(required=True)

    product = graphene.Field(ProductType)
    success = graphene.List(graphene.String)

    @operations_or_master_admin_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('product_id')

        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            raise GraphQLError(
                "Product {} has already been approved".format(id))
        product.is_approved = True
        product.save()
        success = [
            'message',
            'Product {} has successfully been approved.'.format(id)
        ]
        return ApproveProduct(success=success, product=product)


class UpdatePrice(graphene.Mutation):
    products = graphene.List(ProductType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    class Arguments:
        markup = graphene.Int()
        sales_tax = graphene.Float()
        product_ids = graphene.List(graphene.Int)
        auto_price = graphene.Boolean()
        sales_price = graphene.Float()

    @admin_or_manager_required
    def mutate(self, info, **kwargs):
        set_price = SetPrice()
        markup = kwargs.get('markup')
        sales_tax = kwargs.get('sales_tax')
        product_ids = kwargs.get('product_ids')
        auto_price = kwargs.get('auto_price')
        sales_price = kwargs.get('sales_price')
        products = set_price.get_products(product_ids)
        for product in products:
            set_price.update_product_price(
                product, markup=markup,
                sales_tax=sales_tax,
                auto_price=auto_price,
                sales_price=sales_price
            )
        errors = [error.strip('\t')
                  for error in set_price.errors if set_price.errors]
        if errors:
            return UpdatePrice(products=set_price.products, errors=errors)
        return UpdatePrice(
            products=set_price.products,
            message='successfully set prices for products')


class UpdateLoyaltyWeight(graphene.Mutation):
    category = graphene.Field(ProductCategoryType)

    class Arguments:
        product_category_id = graphene.Int(required=True)
        loyalty_value = graphene.Int(required=True)

    message = graphene.String()

    @staticmethod
    @login_required
    @admin_required
    def mutate(self, info, **kwargs):
        loyalty_value = kwargs.get("loyalty_value")
        if loyalty_value < 1:
            raise GraphQLError(
                "Loyalty weight can't be set below one")
        product_category_id = kwargs.get("product_category_id")
        products = ProductQuery().query_product_category(
            product_category_id)
        category = get_model_object(ProductCategory, 'id', product_category_id)
        for product in products:
            product.loyalty_weight = loyalty_value
            product.save()

        message = 'Loyalty weight was successfully updated'
        return UpdateLoyaltyWeight(category=category, message=message)


class UpdateAProductLoyaltyWeight(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        id = graphene.Int(required=True)
        loyalty_value = graphene.Int(required=True)

    message = graphene.String()

    @staticmethod
    @login_required
    @admin_required
    def mutate(self, info, **kwargs):
        loyalty_value = kwargs.get("loyalty_value")
        if loyalty_value < 1:
            raise GraphQLError(
                "Loyalty weight can't be set below one")
        product_id = kwargs.get("id")
        product = get_model_object(Product, 'id', product_id)
        product.loyalty_weight = loyalty_value
        product.save()
        message = 'Loyalty weight was successfully updated'
        return UpdateAProductLoyaltyWeight(product=product, message=message)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_proposed_product = UpdateProposedProduct.Field()
    delete_product = DeleteProduct.Field()
    create_batch_info = CreateBatchInfo.Field()
    update_batch_info = UpdateBatchInfo.Field()
    update_price = UpdatePrice.Field()
    delete_batch_info = DeleteBatchInfo.Field()
    approve_product = ApproveProduct.Field()
    update_loyalty_weight = UpdateLoyaltyWeight.Field()
    product_loyalty_weight_update = UpdateAProductLoyaltyWeight.Field()
