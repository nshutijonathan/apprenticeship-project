import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.notifications.models import Notification
from healthid.apps.notifications.schema.notification_queries import \
    NotificationType
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.notifications_responses import\
     NOTIFICATION_ERROR_RESPONSES, NOTIFICATION_SUCCESS_RESPONSES


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
            success = NOTIFICATION_SUCCESS_RESPONSES[
                      "notification_toggle"].format(
                      'unread' if not record.read_status else 'read')

            return UpdateNotificationReadStatus(notification=notification,
                                                success=success)
        error = NOTIFICATION_ERROR_RESPONSES["notification_validation_error"]
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
            success = (NOTIFICATION_SUCCESS_RESPONSES[
                "notification_deletion_success"].format(id))

            return DeleteNotification(success=success)
        error = NOTIFICATION_ERROR_RESPONSES[
                "notification_validation_deletion_error"]
        return DeleteNotification(error=error)


class Mutation(graphene.ObjectType):
    update_read_status = UpdateNotificationReadStatus.Field()
    delete_notification = DeleteNotification.Field()
