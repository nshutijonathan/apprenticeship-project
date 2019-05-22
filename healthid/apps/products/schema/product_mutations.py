import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import Product, ProductCategory
from healthid.apps.products.schema.batch_info_mutation import (CreateBatchInfo,
                                                               DeleteBatchInfo,
                                                               ProposeQuantity,
                                                               UpdateBatchInfo)
from healthid.apps.products.schema.measurement_unit_mutation import (
    CreateMeasurementUnit, DeleteMeasurementUnit, EditMeasurementUnit)
from healthid.apps.products.schema.product_category_mutation import (
    CreateProductCategory, DeleteProductCategory, EditProductCategory)
from healthid.apps.products.schema.product_query import (
    ProductCategoryType, ProductType)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.query_objects import GetObjectList
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.activate_deactivate_product import \
    activate_deactivate_products
from healthid.utils.product_utils.product import set_attributes
from healthid.utils.product_utils.product_query import ProductQuery
from healthid.utils.product_utils.set_price import SetPrice


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
        prefered_supplier_id = graphene.String()
        backup_supplier_id = graphene.String()
        tags = graphene.List(graphene.String)
        unit_cost = graphene.Float()
        image = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        product = Product()
        output = set_attributes(product, **kwargs)
        return CreateProduct(product=output)


class UpdateProduct(graphene.Mutation):
    """
    update product
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
        image = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            proposed_edit = product
            proposed_edit.id = None
            output = set_attributes(proposed_edit, **kwargs)
            output.parent_id = kwargs.get('id')
            output.save()
            message = 'Proposed update pending approval'
            return UpdateProduct(product=output, message=message)
        output = set_attributes(product, **kwargs)
        message = 'Product successfully updated'
        return UpdateProduct(product=output, message=message)


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


class ApproveProduct(graphene.Mutation):
    """
      Mutation to approve proposed products a product.
    """

    class Arguments:
        product_id = graphene.Int(required=True)

    product = graphene.Field(ProductType)
    success = graphene.List(graphene.String)

    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('product_id')

        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            raise GraphQLError(
                "Product {} has already been approved".format(id))
        product.is_approved = True
        product.save()
        success = [
            'message', 'Product {} has successfully been approved.'.format(id)
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

    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        set_price = SetPrice()
        markup = kwargs.get('markup')
        sales_tax = kwargs.get('sales_tax')
        product_ids = kwargs.get('product_ids')
        auto_price = kwargs.get('auto_price')
        sales_price = kwargs.get('sales_price')
        products = GetObjectList.get_objects(Product, product_ids)
        for product in products:
            set_price.update_product_price(
                product,
                markup=markup,
                sales_tax=sales_tax,
                auto_price=auto_price,
                sales_price=sales_price)
        errors = [
            error.strip('\t') for error in set_price.errors if set_price.errors
        ]
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
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        loyalty_value = kwargs.get("loyalty_value")
        if loyalty_value < 1:
            raise GraphQLError("Loyalty weight can't be set below one")
        product_category_id = kwargs.get("product_category_id")
        products = ProductQuery().query_product_category(product_category_id)
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
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        loyalty_value = kwargs.get("loyalty_value")
        if loyalty_value < 1:
            raise GraphQLError("Loyalty weight can't be set below one")
        product_id = kwargs.get("id")
        product = get_model_object(Product, 'id', product_id)
        product.loyalty_weight = loyalty_value
        product.save()
        message = 'Loyalty weight was successfully updated'
        return UpdateAProductLoyaltyWeight(product=product, message=message)


class ActivateDeactivateProducts(graphene.Mutation):
    class Arguments:
        product_ids = graphene.List(graphene.Int, required=True)

    success = graphene.String()
    products = graphene.List(ProductType)

    def mutate(self, info, **kwargs):
        pass


class ActivateProduct(ActivateDeactivateProducts):
    """
    Mutation class to activate a product
    """
    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        error_msg = \
            'Product with id {product_id} doen\'t exist or is activated.'
        products = activate_deactivate_products(product_ids, False, error_msg)
        success = f'Products with ids {product_ids} have been activated.'
        return ActivateProduct(success=success, products=products)


class DeativateProduct(ActivateDeactivateProducts):
    """
    Mutation class to deactivate a product
    """
    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        error_msg = \
            'Product with id {product_id} doen\'t exist or is deactivated'
        products = activate_deactivate_products(product_ids, True, error_msg)
        success = f'Products with ids {product_ids} have been deactivated.'
        return DeativateProduct(success=success, products=products)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_batch_info = CreateBatchInfo.Field()
    update_batch_info = UpdateBatchInfo.Field()
    proposed_quantity = ProposeQuantity.Field()
    update_price = UpdatePrice.Field()
    delete_batch_info = DeleteBatchInfo.Field()
    approve_product = ApproveProduct.Field()
    update_loyalty_weight = UpdateLoyaltyWeight.Field()
    product_loyalty_weight_update = UpdateAProductLoyaltyWeight.Field()
    deactivate_product = DeativateProduct.Field()
    activate_product = ActivateProduct.Field()
    create_product_category = CreateProductCategory.Field()
    create_measurement_unit = CreateMeasurementUnit.Field()
    edit_product_category = EditProductCategory.Field()
    delete_product_category = DeleteProductCategory.Field()
    edit_measurement_unit = EditMeasurementUnit.Field()
    delete_measurement_unit = DeleteMeasurementUnit.Field()
