import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.notifications.models import Notification
from healthid.apps.notifications.schema.notification_queries import \
    NotificationType
from healthid.utils.app_utils.database import get_model_object


class UpdateNotificationReadStatus(graphene.Mutation):
    """
    Mutation used to mark a notification as read or unread.
    """
    notification = graphene.Field(NotificationType)
    success = graphene.Field(graphene.String)

    class Arguments:
        id = graphene.String(required=True)

    @login_required
    def mutate(self, info, id):
        notification = get_model_object(Notification, 'id', id)
        notification.read_status = not notification.read_status
        success = "Notification was marked as {}.".format(
            'unread' if not notification.read_status else 'read')

        notification.save()
        return UpdateNotificationReadStatus(notification=notification,
                                            success=success)


class DeleteNotification(graphene.Mutation):
    """
    Mutation class to delete a notification.
    """
    success = graphene.Field(graphene.String)
    error = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @login_required
    def mutate(self, info, id):
        recipient = info.context.user
        notification = get_model_object(Notification, 'id', id)
        if notification.recipient == recipient:
            notification.delete()
            success = ("Notification with id {} was successfully deleted."
                       .format(id))

            return DeleteNotification(success=success, error=None)
        error = "You do not have permission to delete this notification!"
        return DeleteNotification(error=error, success=None)


class Mutation(graphene.ObjectType):
    update_read_status = UpdateNotificationReadStatus.Field()
    delete_notification = DeleteNotification.Field()
