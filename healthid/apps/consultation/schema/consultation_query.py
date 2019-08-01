import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.models import (Consultation,
                                               ScheduleConsultation)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT


class ConsultantType(DjangoObjectType):
    class Meta:
        model = Consultation


class ScheduleType(DjangoObjectType):
    class Meta:
        model = ScheduleConsultation


class Query(graphene.ObjectType):
    consultations = graphene.List(
        ConsultantType, page_count=graphene.Int(), page_number=graphene.Int())
    consultation = graphene.Field(
        ConsultantType,
        id=graphene.Int(),
        consultation_name=graphene.String(),
        description=graphene.String(),
        price_per_session=graphene.Int())
    scheduled_consultations = graphene.List(ScheduleType)
    scheduled_consultation = graphene.Field(
        ScheduleType,
        id=graphene.String(),
        customer_name=graphene.String()
    )

    @login_required
    def resolve_consultations(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        consultation_list = Consultation.objects.all()
        if page_count or page_number:
            consultations = pagination_query(
                consultation_list, page_count, page_number)
            return consultations
        return pagination_query(consultation_list,
                                PAGINATION_DEFAULT["page_count"],
                                PAGINATION_DEFAULT["page_number"])

    @login_required
    def resolve_consultation(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return get_model_object(Consultation, 'id', id)
        return None

    @login_required
    def resolve_scheduled_consultations(self, info, **kwargs):
        return ScheduleConsultation.objects.all()

    @login_required
    def resolve_scheduled_consultation(self, info, id):
        return get_model_object(ScheduleConsultation, 'id', id)
