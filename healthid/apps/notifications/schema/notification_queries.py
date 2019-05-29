import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.notifications.models import Notification
from graphql import GraphQLError


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification


class Query(graphene.ObjectType):
    notifications = graphene.List(NotificationType)

    @login_required
    def resolve_notifications(self, info, **kwargs):
        user = info.context.user

        notifications = Notification.objects.filter(
            notification_records__recipient=user)
        if notifications:
            return notifications
        raise GraphQLError('Oops! There are no notifications yet!')
