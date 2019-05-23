import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import PriceCheckSurvey, Product, Survey
from healthid.apps.products.schema.product_query import SurveyType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.validators import validate_empty_field
from healthid.utils.auth_utils.decorator import user_permission


class SupplierType(DjangoObjectType):
    """Supplier type class"""
    class Meta:
        model = Suppliers


class PriceCheckSurveyType(DjangoObjectType):
    """Type for price check surveys"""
    class Meta:
        model = PriceCheckSurvey


class CreatePriceCheckSurvey(graphene.Mutation):
    """Mutation class for creating a survey for supplier price checks."""
    survey = graphene.Field(SurveyType)
    success = graphene.String()

    class Arguments:

        name = graphene.String(required=True)
        outlet_id = graphene.Int(required=True)
        suppliers = graphene.List(graphene.String, required=True)
        products = graphene.List(graphene.Int, required=True)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        validate_empty_field('name', name)
        suppliers = kwargs.get('suppliers')
        products = kwargs.get('products')
        created_by = info.context.user

        outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        survey_instance = Survey(
            created_by=created_by, outlet=outlet, name=name)

        params = {
            'model_name': 'Survey',
            'field': 'name',
            'value': name
        }

        # Save the survey instance along with the products and suppliers
        with SaveContextManager(survey_instance, **params):
            for supplier_id in suppliers:
                supplier = get_model_object(
                    Suppliers, 'supplier_id', supplier_id)
                for product_id in products:
                    price_check_survey = PriceCheckSurvey()
                    price_check_survey.supplier = supplier
                    product = get_model_object(Product, 'id', product_id)
                    price_check_survey.product = product
                    price_check_survey.save()
                    price_check_survey.survey.add(survey_instance)

            success = 'Master survey, {}, successfully created.'.format(name)
            return CreatePriceCheckSurvey(success=success,
                                          survey=survey_instance)


class DeletePriceCheckSurvey(graphene.Mutation):
    """
    Mutation to delete an existing master survey.
    This mutation implements soft delete.
    """
    success = graphene.String()

    class Arguments:
        survey_id = graphene.String(required=True)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        survey_id = kwargs.get("survey_id")
        validate_empty_field('Survey Id', survey_id)

        # get survey instance and unlink all its
        # price_check_survey instances
        survey = get_model_object(Survey, 'id', survey_id)
        survey.survey_price_checks.all().delete()
        survey.delete()

        message = 'Survey id, {}, and all its associated price '.format(
            survey_id)
        message += 'checks have been deleted!'
        return DeletePriceCheckSurvey(success=message)


class UpdatePriceCheckSurvey(graphene.Mutation):
    """
    Mutation to update an existing price
    check survey.
    """
    survey = graphene.Field(SurveyType)
    success = graphene.String()

    class Arguments:

        survey_id = graphene.String(required=True)
        name = graphene.String()
        suppliers = graphene.List(graphene.String)
        products = graphene.List(graphene.Int)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        suppliers = kwargs.get('suppliers')
        products = kwargs.get('products')
        survey_id = kwargs.get('survey_id')
        validate_empty_field('Survey Id', survey_id)

        # find survey and check if it is still open.
        survey_instance = get_model_object(Survey, 'id', survey_id)
        if survey_instance.survey_closed:
            raise GraphQLError('This survey has already been closed. '
                               ' It cannot be updated!')

        # update survey name if it has been provided.
        if name:
            survey_instance.name = name

        params = {
            'model_name': 'Survey',
            'field': 'name',
            'value': name
        }

        with SaveContextManager(survey_instance, **params):
            if suppliers and not products:
                raise GraphQLError(
                    "Please specify at least one product.")
            if products and not suppliers:
                raise GraphQLError(
                    "Please specify at least one supplier.")
                # delete all price checks for the current survey
                # since no other survey will be using them
                # after disassociating them with the current survey.

            survey_instance.survey_price_checks.all().delete()

            # create new price checks for the current survey.
            for supplier_id in suppliers:
                supplier = get_model_object(
                    Suppliers, 'supplier_id', supplier_id)
                for product_id in products:
                    price_check_survey = PriceCheckSurvey()
                    product = get_model_object(
                        Product, 'id', product_id)
                    price_check_survey.supplier = supplier
                    price_check_survey.product = product
                    price_check_survey.save()
                    price_check_survey.survey.add(survey_instance)

        success = 'Survey, {}, successfully updated.'.format(
            survey_instance.id)
        return UpdatePriceCheckSurvey(success=success,
                                      survey=survey_instance)
