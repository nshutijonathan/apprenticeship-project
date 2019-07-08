import graphene
from django.template.loader import render_to_string
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import User
from healthid.apps.consultation.models import (Consultation,
                                               ScheduleConsultation)
from healthid.apps.consultation.schema.consultation_query import ScheduleType
from healthid.apps.events.models import Event
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.notifications_utils.handle_notifications import \
    send_email_to
from healthid.utils.messages.consultation_reponses import\
    CONSULTATION_SUCCESS_RESPONSES


class PaymentStatusEnum(graphene.Enum):
    PAID = 'Paid'
    NOT_PAID = 'Not paid'


class Schedule(graphene.Mutation):
    """Schedule consultation with Pharmacy."""
    schedule_consultation = graphene.Field(ScheduleType)
    success = graphene.String()

    class Arguments:
        consultation_type_id = graphene.Int(required=True)
        customer_name = graphene.String(required=True)
        payment_status = graphene.Argument(PaymentStatusEnum, required=True)
        consultants = graphene.List(graphene.String)
        start_date = graphene.Date(required=True)
        end_date = graphene.Date(required=True)
        start_time = graphene.Time(required=True)
        end_time = graphene.Time(required=True)
        email = graphene.String(required=True)
        event_type_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        schedule_consultation = ScheduleConsultation()
        consultant_ids = kwargs.pop('consultants')
        start_date = kwargs.pop('start_date')
        end_date = kwargs.pop('end_date')
        start_time = kwargs.pop('start_time')
        end_time = kwargs.pop('end_time')
        email = kwargs.pop('email')
        event_type_id = kwargs.pop('event_type_id')
        valid_consultants = [get_model_object(
            User, 'id', consultant_id) for consultant_id in consultant_ids]

        for (key, value) in kwargs.items():
            if key in ('customer_name', 'payment_status') and \
                    value.strip() == "":
                raise GraphQLError("The {} field can't be empty".format(key))
            setattr(schedule_consultation, key, value)
        with SaveContextManager(schedule_consultation) as consultation:
            consultation.consultants.add(*valid_consultants)
            event = Event(
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
                event_title=f'Consultation for {consultation.customer_name}',
                description=f'Consultation id: {consultation.id}',
                event_type_id=event_type_id
            )
            with SaveContextManager(event) as event:
                event.save()
            consultation.event = event
            consultation.save()
            consultation_type = get_model_object(
                Consultation, 'id', consultation.consultation_type_id)
            success =\
                CONSULTATION_SUCCESS_RESPONSES["consultation_schedule_success"]
            context = {
                'template_type': 'Schedule Consultation',
                'small_text_detail': success,
                'email': email,
                'outlet_name': consultation_type.outlet.name,
                'start_date': start_date,
                'start_time': start_time,
                'first_name': info.context.user.first_name}
            html_body = render_to_string(
                'email_alerts/schedule_consultation.html', context)
            send_email_to('Consultation scheduled', email, html_body)
            return Schedule(
                success=success, schedule_consultation=consultation)
