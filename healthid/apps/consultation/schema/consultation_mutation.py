import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.consultation.models import Consultation
from healthid.apps.outlets.models import Outlet
from healthid.apps.consultation.schema.consultation_query import ConsultantType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission


class CreateConsultation(graphene.Mutation):
    consultation = graphene.Field(ConsultantType)

    class Arguments:
        consultation_name = graphene.String()
        description = graphene.String()
        approved_delivery_formats_id = graphene.Int()
        expected_time_id = graphene.Int()
        consultant_role_id = graphene.Int()
        outlet_id = graphene.Int()
        price_per_session = graphene.Int()

    success = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admins')
    def mutate(self, info, **kwargs):
        consultation = Consultation()
        get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        for (key, value) in kwargs.items():
            if type(value) is str and value.strip() == "":
                raise GraphQLError("The {} field can't be empty".format(key))
            setattr(consultation, key, value)
        params = {
            'model_name': 'Consultation',
            'field': 'consultation_name',
            'value': kwargs.get('consultation_name')
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
        consultation.save()
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
        consultation = get_model_object(Consultation, 'id', id)
        consultation.delete()
        message = ["Consultation deleted successfully!"]
        return DeleteConsultation(message=message)


class Mutation(graphene.ObjectType):
    create_consultation = CreateConsultation.Field()
    edit_consultation = EditConsultation.Field()
    delete_consultation = DeleteConsultation.Field()
