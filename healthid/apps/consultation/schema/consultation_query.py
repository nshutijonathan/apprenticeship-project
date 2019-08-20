import graphene

from healthid.apps.consultation.models import (
    ConsultationCatalogue)
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.schema.consultation_schema import (
    ConsultationCatalogueType)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.messages.consultation_reponses import \
    CONSULTATION_ERROR_RESPONSES
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT


class Query(graphene.ObjectType):
    consultations = graphene.List(ConsultationCatalogueType)
    consultation = graphene.Field(
        ConsultationCatalogueType,
        consultation_id=graphene.Int(),
        consultation_name=graphene.String(),
        description=graphene.String(),
        price_per_session=graphene.Int(),
        approved_delivery_format=graphene.String(),
        consultant_role=graphene.String(),
        minutes_per_session=graphene.Int()
    )

    @login_required
    def resolve_consultations(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user = info.context.user
        all_consultations = ConsultationCatalogue.objects.filter(
            outlet=user.active_outlet)
        if page_count or page_number:
            consultations = pagination_query(
                all_consultations, page_count, page_number)
            return consultations
        return pagination_query(all_consultations,
                                PAGINATION_DEFAULT["page_count"],
                                PAGINATION_DEFAULT["page_number"])

    @login_required
    def resolve_consultation(self, info, **kwargs):
        consultation_id = kwargs.get("consultation_id")
        user = info.context.user
        if consultation_id > 0:
            consultation = get_model_object(
                ConsultationCatalogue, 'id', consultation_id)
            if consultation.outlet.id != user.active_outlet.id:
                consultation_query_error =\
                    CONSULTATION_ERROR_RESPONSES[
                        "consultation_doesnot_exist_error"]
                raise GraphQLError(consultation_query_error)
            return consultation
        consultation_error =\
            CONSULTATION_ERROR_RESPONSES[
                "invalid_id"].format("Consultation")
        raise GraphQLError(consultation_error)
