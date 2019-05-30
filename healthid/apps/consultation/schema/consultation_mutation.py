import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.models import Consultation
from healthid.apps.consultation.schema.consultation_query import ConsultantType
from healthid.apps.consultation.schema.schedule_consultation_mutation import \
    Schedule
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission


class CreateConsultation(graphene.Mutation):
    consultation = graphene.Field(ConsultantType)

    class Arguments:
        consultation_name = graphene.String(required=True)
        description = graphene.String(required=True)
        approved_delivery_formats_id = graphene.Int(required=True)
        expected_time_id = graphene.Int(required=True)
        consultant_role_id = graphene.Int(required=True)
        outlet_id = graphene.Int(required=True)
        price_per_session = graphene.Int(required=True)

    success = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admins')
    def mutate(self, info, **kwargs):
        get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        name = kwargs.get('consultation_name')
        consultation = Consultation()
        for (key, value) in kwargs.items():
            if type(value) is str and value.strip() == "":
                raise GraphQLError("The {} field can't be empty".format(key))
            setattr(consultation, key, value)
        params = {
            'model': Consultation, 'field': 'consultation_name', 'value': name
        }
        with SaveContextManager(consultation, **params) as consultation:
            success = ["consultation type has succesfully been created"]
            return CreateConsultation(
                success=success, consultation=consultation)


class EditConsultation(graphene.Mutation):
    """
    update conultation
    """
    consultation = graphene.Field(ConsultantType)

    class Arguments:
        id = graphene.Int()
        consultation_name = graphene.String()
        description = graphene.String()
        approved_delivery_formats_id = graphene.Int()
        expected_time_id = graphene.Int()
        consultant_role_id = graphene.Int()
        outlet_id = graphene.Int()
        price_per_session = graphene.Int()

    message = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs['id']
        consultation = get_model_object(Consultation, 'id', id)

        for key, value in kwargs.items():
            if key is not None:
                setattr(consultation, key, value)
        params = {
            'model': Consultation, 'field': 'consultation_name',
            'value': consultation.consultation_name
        }
        with SaveContextManager(consultation, **params) as consultation:
            message = ["consultation updated successfully!"]
            return EditConsultation(consultation=consultation, message=message)


class DeleteConsultation(graphene.Mutation):
    """
        Delete consultation
    """
    consultation = graphene.Field(ConsultantType)

    class Arguments:
        id = graphene.Int()

    message = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, id):
        user = info.context.user
        consultation = get_model_object(Consultation, 'id', id)
        consultation.delete(user)
        message = ["Consultation deleted successfully!"]
        return DeleteConsultation(message=message)


class Mutation(graphene.ObjectType):
    create_consultation = CreateConsultation.Field()
    edit_consultation = EditConsultation.Field()
    delete_consultation = DeleteConsultation.Field()
    schedule = Schedule.Field()
