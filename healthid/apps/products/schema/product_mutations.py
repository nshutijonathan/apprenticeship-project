import graphene
from django.forms.models import model_to_dict
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import Product, ProductCategory
from healthid.apps.products.schema.batch_info_mutation import (
    ApproveProposedQuantity, CreateBatchInfo, DeleteBatchInfo, ProposeQuantity,
    UpdateBatchInfo)
from healthid.apps.products.schema.measurement_unit_mutation import (
    CreateMeasurementUnit, DeleteMeasurementUnit, EditMeasurementUnit)
from healthid.apps.products.schema.price_survey_mutations import (
    CreatePriceCheckSurvey, DeletePriceCheckSurvey, UpdatePriceCheckSurvey)
from healthid.apps.products.schema.product_category_mutation import (
    CreateProductCategory, DeleteProductCategory, EditProductCategory)
from healthid.apps.products.schema.product_query import (ProductCategoryType,
                                                         ProductType)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.query_objects import GetObjectList
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.activate_deactivate_product import \
    activate_deactivate_products
from healthid.utils.product_utils.product import set_product_attributes
from healthid.utils.product_utils.product_query import ProductQuery
from healthid.utils.product_utils.set_price import SetPrice
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import\
     PRODUCTS_ERROR_RESPONSES, PRODUCTS_SUCCESS_RESPONSES


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
        product_name = graphene.String(required=True)
        description = graphene.String(required=True)
        product_category_id = graphene.Int(required=True)
        brand = graphene.String(required=True)
        manufacturer = graphene.String(required=True)
        measurement_unit_id = graphene.Int(required=True)
        preferred_supplier_id = graphene.String()
        backup_supplier_id = graphene.String()
        vat_status = graphene.Boolean(required=True)
        loyalty_weight = graphene.Int(required=True)
        image = graphene.String()
        tags = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        product = Product()
        product.markup = get_model_object(
            ProductCategory, 'id', kwargs.get('product_category_id')).markup
        product = set_product_attributes(product, **kwargs)
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    """
    update product
    """
    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        product_name = graphene.String()
        description = graphene.String()
        product_category_id = graphene.Int()
        brand = graphene.String()
        manufacturer = graphene.String()
        measurement_unit_id = graphene.Int()
        preferred_supplier_id = graphene.String()
        backup_supplier_id = graphene.String()
        vat_status = graphene.Boolean()
        loyalty_weight = graphene.Int()
        markup = graphene.Int()
        image = graphene.String()
        tags = graphene.List(graphene.String)
        sku_number = graphene.Int()
        auto_price = graphene.Boolean()
        sales_price = graphene.Int()
        nearest_expiry_date = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            proposed_edit = product
            proposed_edit.id = None
            output = set_product_attributes(proposed_edit, **kwargs)
            output.parent_id = kwargs.get('id')
            output.is_approved = False
            output.user = user
            output.save()
            message = PRODUCTS_SUCCESS_RESPONSES["approval_pending"]
            return UpdateProduct(product=output, message=message)
        output = set_product_attributes(product, **kwargs)
        message = SUCCESS_RESPONSES["update_success"].format("Product")
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
        user = info.context.user
        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            raise GraphQLError(
                  PRODUCTS_ERROR_RESPONSES["approve_deletion_error"])
        product.delete(user)

        return DeleteProduct(
               success=SUCCESS_RESPONSES["deletion_success"].format("Product"))


class ApproveProduct(graphene.Mutation):
    """
      Mutation to approve proposed products.
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
               PRODUCTS_ERROR_RESPONSES[
                   "product_approval_duplication"].format(id))
        product.is_approved = True
        product.save()
        success = [
            'message',
            SUCCESS_RESPONSES["approval_success"].format("Product " + str(id))
        ]
        return ApproveProduct(success=success, product=product)


class ApproveProposedEdits(graphene.Mutation):
    class Arguments:
        edit_request_id = graphene.Int(required=True)

    product = graphene.Field(ProductType)
    message = graphene.List(graphene.String)

    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        request_id = kwargs.get('edit_request_id')
        message = PRODUCTS_ERROR_RESPONSES[
                  "inexistent_proposed_edit"].format(request_id)

        proposed_edit = get_model_object(
            Product, 'id', request_id, message=message)
        message = f"No product with  proposed edit with id {request_id}"
        parent = get_model_object(
            Product, 'id', proposed_edit.parent_id, message=message)
        product_dict = model_to_dict(proposed_edit)
        exclude_list = [
            'auto_price', 'parent', 'is_active', 'is_approved', 'sku_number',
            'user', 'outlet'
        ]
        [product_dict.pop(item) for item in exclude_list]
        product_dict['preferred_supplier_id'] = product_dict.pop(
            'preferred_supplier')
        product_dict['backup_supplier_id'] = product_dict.pop(
            'backup_supplier')
        product_dict['product_category_id'] = product_dict.pop(
            'product_category')
        product_dict['measurement_unit_id'] = product_dict.pop(
            'measurement_unit')
        product_dict.pop('id')
        for key, value in product_dict.items():
            if value is not None:
                setattr(parent, key, value)
        proposed_edit.hard_delete()
        parent.save()
        message = [SUCCESS_RESPONSES["approval_success"].format(
                                                         "Edit request")]
        return ApproveProposedEdits(product=parent, message=message)


class DeclineProposedEdits(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        comment = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    edit_request = graphene.Field(ProductType)

    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        message = "No proposed edit with id {id}"
        comment = kwargs.get('comment')
        edit_request = get_model_object(Product, 'id', id, message=message)
        edit_request.admin_comment = comment
        edit_request.save()
        product_name = edit_request.product_name
        msg = PRODUCTS_SUCCESS_RESPONSES[
              "edit_request_decline"].format(product_name)
        return DeclineProposedEdits(message=msg, edit_request=edit_request)


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
            message=PRODUCTS_SUCCESS_RESPONSES["set_price_success"])


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
            raise GraphQLError(
                  PRODUCTS_ERROR_RESPONSES["loyalty_weight_error"])
        product_category_id = kwargs.get("product_category_id")
        products = ProductQuery().query_product_category(product_category_id)
        category = get_model_object(ProductCategory, 'id', product_category_id)
        for product in products:
            product.loyalty_weight = loyalty_value
            product.save()

        message = SUCCESS_RESPONSES["update_success"].format("Loyalty weight")
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
            raise GraphQLError(
                  PRODUCTS_ERROR_RESPONSES["loyalty_weight_error"])
        product_id = kwargs.get("id")
        product = get_model_object(Product, 'id', product_id)
        product.loyalty_weight = loyalty_value
        product.save()
        message = SUCCESS_RESPONSES["update_success"].format("Loyalty weight")
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
        error_msg = PRODUCTS_ERROR_RESPONSES[
                    "product_activation_error"].format(product_ids)
        products = activate_deactivate_products(product_ids, False, error_msg)
        success = PRODUCTS_SUCCESS_RESPONSES[
                  "product_activation_success"].format(product_ids)
        return ActivateProduct(success=success, products=products)


class DeativateProduct(ActivateDeactivateProducts):
    """
    Mutation class to deactivate a product
    """

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        error_msg = PRODUCTS_ERROR_RESPONSES[
                    "product_deactivation_error"].format(product_ids)
        products = activate_deactivate_products(product_ids, True, error_msg)
        success = PRODUCTS_SUCCESS_RESPONSES[
                  "product_deactivation_success"].format(product_ids)
        return DeativateProduct(success=success, products=products)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_batch_info = CreateBatchInfo.Field()
    update_batch_info = UpdateBatchInfo.Field()
    proposed_quantity = ProposeQuantity.Field()
    approve_quantity = ApproveProposedQuantity.Field()
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
    create_price_check_survey = CreatePriceCheckSurvey.Field()
    delete_price_check_survey = DeletePriceCheckSurvey.Field()
    update_price_check_survey = UpdatePriceCheckSurvey.Field()
    approve_proposed_edits = ApproveProposedEdits.Field()
    decline_proposed_edits = DeclineProposedEdits.Field()
