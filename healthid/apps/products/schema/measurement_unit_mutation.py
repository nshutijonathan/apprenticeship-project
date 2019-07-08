import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.products.models import MeasurementUnit
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission

from .product_query import MeasurementUnitType
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class CreateMeasurementUnit(graphene.Mutation):
    """
        Mutation to create a Measurement Unit
    """
    measurement_unit = graphene.Field(MeasurementUnitType)

    class Arguments:
        name = graphene.String(required=True)

    message = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(PRODUCTS_ERROR_RESPONSES["invalid_input_error"])
        measurement_unit = MeasurementUnit(name=name)
        with SaveContextManager(measurement_unit, model=MeasurementUnit):
            message = [SUCCESS_RESPONSES[
                       "creation_success"].format("Measurement Unit")]
            return CreateMeasurementUnit(
                message=message, measurement_unit=measurement_unit)


class EditMeasurementUnit(graphene.Mutation):
    """
    update measuremnt unit
    """
    measuremnt_unit = graphene.Field(MeasurementUnitType)
    message = graphene.String()

    class Arguments:
        name = graphene.String()
        id = graphene.Int()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(PRODUCTS_ERROR_RESPONSES["invalid_input_error"])
        measuremnt_unit = get_model_object(MeasurementUnit, 'id', id)
        measuremnt_unit.name = name
        with SaveContextManager(measuremnt_unit, model=MeasurementUnit):
            message = SUCCESS_RESPONSES[
                      "update_success"].format(
                                        "Measuremnt Unit of Id " + str(id))
            return EditMeasurementUnit(
                measuremnt_unit=measuremnt_unit, message=message)


class DeleteMeasurementUnit(graphene.Mutation):
    """
        Delete a measurement unit
    """
    measurement_unit = graphene.Field(MeasurementUnitType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        user = info.context.user
        measurement_unit = get_model_object(MeasurementUnit, 'id', id)
        measurement_unit.delete(user)
        success = SUCCESS_RESPONSES[
                      "deletion_success"].format(
                                          "Measuremnt Unit of Id " + str(id))
        return DeleteMeasurementUnit(success=success)
