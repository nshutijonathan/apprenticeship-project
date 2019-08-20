import graphene

from healthid.apps.consultation.schema.consultation_schema import (
    CustomerConsultationType)
from healthid.apps.consultation.schema.consultation_schema import (
    CustomerConsultation)
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.messages.consultation_reponses import \
    CONSULTATION_ERROR_RESPONSES
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.app_utils.database import get_model_object


class Query(graphene.ObjectType):
    bookings = graphene.List(CustomerConsultationType)
    booking = graphene.Field(
        CustomerConsultationType,
        id=graphene.Int(),
        customer_id=graphene.Int(),
        booked_by_id=graphene.String(),
        status=graphene.String(),
        consultation_type_id=graphene.Int(),
        consultant=graphene.String(),
        booking_date=graphene.Date()
    )

    @login_required
    def resolve_bookings(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        all_customer_consultations = CustomerConsultation.objects.all()
        if page_count or page_number:
            customer_consultations = pagination_query(
                all_customer_consultations, page_count, page_number)
            return customer_consultations
        return pagination_query(all_customer_consultations,
                                PAGINATION_DEFAULT["page_count"],
                                PAGINATION_DEFAULT["page_number"])

    @login_required
    def resolve_booking(self, info, **kwargs):
        customer_id = kwargs.get("id")
        if customer_id > 0:
            booking = get_model_object(
                CustomerConsultation, 'id', customer_id)
            return booking
        customer = CONSULTATION_ERROR_RESPONSES["invalid_id"].format("Booking")
        raise GraphQLError(customer)
