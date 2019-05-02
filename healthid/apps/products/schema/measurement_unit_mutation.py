import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.products.models import MeasurementUnit
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission

from .product_query import MeasurementUnitType


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
            raise GraphQLError("This name field can't be empty")
        params = {
            'model_name': 'MeasurementUnit',
            'field': 'name',
            'value': name
        }
        measurement_unit = MeasurementUnit(name=name)
        with SaveContextManager(measurement_unit, **params):
            message = [f'Measurement unit created succesfully']
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
            raise GraphQLError("The name field can't be empty")
        measuremnt_unit = get_model_object(MeasurementUnit, 'id', id)
        measuremnt_unit.name = name
        params = {'model_name': 'MeasurementUnit', 'value': name}
        with SaveContextManager(measuremnt_unit, **params):
            message = f'Measuremnt Unit of Id {id} is successfully updated'
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
        measurement_unit = get_model_object(MeasurementUnit, 'id', id)
        measurement_unit.delete()
        success = f'Measurement unit of Id {id} \
            has been successfully deleted'

        return DeleteMeasurementUnit(success=success)
