from datetime import datetime

import graphene
from django.core.exceptions import ValidationError
from graphene.utils.resolve_only_args import resolve_only_args
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from taggit.managers import TaggableManager

from healthid.apps.products.models import (BatchInfo, MeasurementUnit, Product,
                                           ProductCategory, Quantity, Survey)
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return graphene.List(graphene.String, source='get_tags')


class BatchInfoType(DjangoObjectType):
    quantity = graphene.Int()
    proposed_quantity = graphene.Int()

    class Meta:
        model = BatchInfo

    def resolve_quantity(self, info, **kwargs):
        return self.quantity

    def resolver_proposed_quantity(self, info, **kwargs):
        return self.proposed_quantity


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory


class MeasurementUnitType(DjangoObjectType):
    class Meta:
        model = MeasurementUnit


class ProductType(DjangoObjectType):
    product_quantity = graphene.Int()
    autofill_quantity = graphene.Int()
    sales_price = graphene.Float()
    pre_tax_retail_price = graphene.Float()
    unit_cost = graphene.Int()

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
        return self.quantity

    @resolve_only_args
    def resolve_sales_price(self):
        return self.get_sales_price

    def resolve_pre_tax_retail_price(self, info, **kwargs):
        return self.pre_tax_retail_price

    def resolve_unit_cost(self,  info, **kwargs):
        return self.avarage_unit_cost

    def resolve_autofill_quantity(self, info, **kwargs):
        return self.autofill_quantity

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class QuantityType(DjangoObjectType):
    id = graphene.String()
    quantity_received = graphene.Int()

    class Meta:
        model = Quantity


class SurveyType(DjangoObjectType):
    class Meta:
        model = Survey


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
    price_check_surveys = graphene.List(SurveyType)
    price_check_survey = graphene.Field(
        SurveyType, id=graphene.String(required=True))
    user_product_requests = graphene.List(ProductType)
    approved_quantities = graphene.List(QuantityType)
    declined_quantities = graphene. List(QuantityType)

    product_autofill = graphene.List(ProductType)
    product = graphene.Field(
        ProductType,
        id=graphene.Int(),
        product_name=graphene.String(),
        sku_number=graphene.Int(),
        description=graphene.String(),
        brand=graphene.String(),
        manufacturer=graphene.String(),
        sales_price=graphene.Int(),
        nearest_expiry_date=graphene.String(),
        tags=graphene.List(graphene.String))

    batch_expiries = graphene.Field(
        product_batch_info,
        start_date=graphene.String(),
        end_date=graphene.String(required=True))
    expired_batches = graphene.Field(product_batch_info)
    deactivated_products = graphene.List(ProductType)
    product_categories = graphene.List(
        ProductCategoryType, outlet_id=graphene.Int(required=True))
    measurement_unit = graphene.List(MeasurementUnitType)

    @login_required
    def resolve_products(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        return Product.all_products.for_outlet(
            outlet.id).filter(parent_id__isnull=True)

    @login_required
    def resolve_filter_products(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        for key in kwargs:
            if isinstance(kwargs[key], str) and kwargs[key].strip() == "":
                raise GraphQLError(
                    PRODUCTS_ERROR_RESPONSES["invalid_search_key"])

        approved_products = Product.all_products.for_outlet(outlet.id).filter(
            parent_id__isnull=True)
        response = approved_products.filter(**kwargs).order_by("product_name")
        if not response:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["inexistent_product_query"])
        return response

    @login_required
    def resolve_proposed_products(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        return Product.all_products.for_outlet(outlet.id).filter(
            is_approved=False, parent_id__isnull=True)

    @login_required
    def resolve_approved_products(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        return Product.objects.for_outlet(outlet.id).filter(is_approved=True)

    @login_required
    def resolve_product(self, info, **kwargs):
        id = kwargs.get('id')
        if id:
            return get_model_object(Product, 'id', id)
        raise GraphQLError(ERROR_RESPONSES["invalid_field_error"].format(id))

    @login_required
    def resolve_proposed_edits(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        return Product.all_products.for_outlet(outlet.id).exclude(
            parent_id__isnull=True)

    @login_required
    def resolve_product_categories(self, info, **kwargs):
        outlet_id = kwargs.get('outlet_id')
        return ProductCategory.objects.filter(outlet_id=outlet_id)

    @login_required
    def resolve_measurement_unit(self, info):
        return MeasurementUnit.objects.all()

    @login_required
    def resolve_price_check_surveys(self, info):
        return Survey.objects.all()

    @login_required
    def resolve_price_check_survey(self, info, **kwargs):
        return get_model_object(Survey, 'id', kwargs.get('id'))

    @login_required
    def resolve_user_product_requests(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        return Product.all_products.for_outlet(outlet.id).filter(
            user=user).exclude(parent=None)

    @login_required
    def resolve_product_autofill(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        product_list = []
        for product in Product.objects.for_outlet(outlet.id):
            if product.quantity < product.reorder_point:
                product_list.append(product)
        return product_list


class BatchQuery(graphene.AbstractType):
    all_batch_info = graphene.List(BatchInfoType)
    batch_info = graphene.Field(
        BatchInfoType, id=graphene.String(required=True))
    batch_quantity = graphene.Field(
        QuantityType, id=graphene.String(required=True))
    product_batch_info = graphene.List(
        BatchInfoType, id=graphene.Int(required=True))
    proposed_quantity_edits = graphene.List(QuantityType)

    @login_required
    def resolve_all_batch_info(self, info):
        return BatchInfo.objects.all()

    @login_required
    def resolve_batch_info(self, info, **kwargs):
        id = kwargs.get('id')
        batch = get_model_object(BatchInfo, 'id', id)
        return batch

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
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        return Product.all_products.for_outlet(outlet.id).filter(
            is_active=False)

    @login_required
    @user_permission('Manager', 'Operations Admin')
    def resolve_proposed_quantity_edits(self, info):
        return Quantity().get_proposed_quantities()

    @login_required
    @user_permission('Operations Admin')
    def resolve_approved_quantities(self, info):
        return Quantity.objects.filter(
            parent_id__isnull=True, is_approved=True)

    @login_required
    @user_permission('Operations Admin')
    def resolve_declined_quantities(self, info):
        return Quantity.objects.filter(
            parent_id__isnull=True, request_declined=True)
