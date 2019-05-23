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
    error = graphene.Field(graphene.String)

    class Arguments:
        id = graphene.String(required=True)

    @login_required
    def mutate(self, info, id):
        recipient = info.context.user
        notification = get_model_object(Notification, 'id', id)
        notification_record = notification.notification_records.filter(
            recipient=recipient)
        if notification_record:
            record = notification_record[0]
            record.read_status = not record.read_status
            record.save()
            success = "Notification was marked as {}.".format(
                'unread' if not record.read_status else 'read')

            return UpdateNotificationReadStatus(notification=notification,
                                                success=success)
        error = "You are not among the recipients for this notification!"
        return UpdateNotificationReadStatus(error=error)


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
        notification_record = notification.notification_records.filter(
            recipient=recipient)

        if notification_record:
            record = notification_record[0]
            record.notification.clear()
            success = ("Notification with id {} was successfully deleted."
                       .format(id))

            return DeleteNotification(success=success)
        error = "You cannot delete this notification \
since you are not a recipient!"
        return DeleteNotification(error=error)


class Mutation(graphene.ObjectType):
    update_read_status = UpdateNotificationReadStatus.Field()
    delete_notification = DeleteNotification.Field()
