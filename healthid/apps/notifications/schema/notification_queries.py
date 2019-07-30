import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.notifications.models import Notification
from graphql import GraphQLError
from healthid.utils.messages.notifications_responses import\
     NOTIFICATION_ERROR_RESPONSES


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification


class Query(graphene.ObjectType):
    """
    Queries notification messages where the user is a recipient

    returns:
            list of 'Notification' objects
    """
    notifications = graphene.List(NotificationType)

    @login_required
    def resolve_notifications(self, info, **kwargs):
        user = info.context.user
        notifications = Notification.objects.filter(
            notification_records__recipient=user)
        if notifications:
            return notifications
        raise GraphQLError(NOTIFICATION_ERROR_RESPONSES["empty_notifications"])
