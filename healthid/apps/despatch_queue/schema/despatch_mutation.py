import graphene
from datetime import datetime
from django.utils.timezone import make_aware
from graphene_django import DjangoObjectType
from healthid.apps.authentication.models import User
from graphql_jwt.decorators import login_required
from healthid.apps.despatch_queue.models import DespatchQueue
from healthid.utils.despatch_util.despatch_email_util import notify
from healthid.utils.app_utils.database import get_model_object


class DespatchQueueType(DjangoObjectType):
    class Meta:
        model = DespatchQueue


class CreateEmailNotifications(graphene.Mutation):
    """
    Mutation used to create email notiffications despatch.
    """
    queues = graphene.Field(graphene.List(of_type=DespatchQueueType))

    class Arguments:
        recipient_ids = graphene.List(required=True, of_type=graphene.String)
        subject = graphene.String(required=True)
        body = graphene.String(required=True)
        due_date = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        recipients_ids = kwargs.get('recipient_ids')
        users = list(map(lambda recipients_id: get_model_object(
            User, 'id', recipients_id), recipients_ids))
        despatch_queue = DespatchQueue()
        due_date = kwargs.get('due_date')
        if not due_date:
            due_date = despatch_queue.add_due_date

        try:
            due_date = make_aware(datetime.strptime(
                str(due_date), '%Y-%m-%d %H:%M:%S'))
        except ValueError as error:
            return error
        despatch_qs = notify(
            users=users,
            subject=kwargs.get('subject'),
            body=kwargs.get('body'),
            due_date=due_date
        )
        return CreateEmailNotifications(queues=despatch_qs)


class Mutation(graphene.ObjectType):
    create_email_notifications = CreateEmailNotifications.Field()
