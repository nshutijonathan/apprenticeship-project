import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.events.models import Event
from healthid.apps.events.models import EventType as EventTypeModel
from healthid.utils.events_utils.validate_role import ValidateAdmin
from healthid.apps.outlets.models import Outlet
from healthid.utils.auth_utils.decorator import master_admin_required


class EventType(DjangoObjectType):
    class Meta:
        model = Event


class EventsTypeType(DjangoObjectType):
    class Meta:
        model = EventTypeModel


class CreateEvent(graphene.Mutation):
    """Mutation creates an event on a calendar.
    """
    event = graphene.Field(EventType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        event_type_id = graphene.String(required=True)
        start = graphene.Date(required=True)
        end = graphene.Date(required=True)
        event_title = graphene.String(required=True)
        description = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user

        try:
            outlet = Outlet.objects.get(user=user)
        except Outlet.DoesNotExist:
            raise GraphQLError("Sorry, calendar is only used by outlet staff!")
        event_type = kwargs.get('event_type')
        ValidateAdmin().validate_master_admin(user, event_type)
        try:
            EventTypeModel.objects.get(id=kwargs.get('event_type_id'))
        except EventTypeModel.DoesNotExist:
            raise GraphQLError('Event Type does not exist!')
        event = Event.objects.create(
            event_type_id=kwargs.get('event_type_id'),
            start=kwargs.get('start'),
            end=kwargs.get('end'),
            event_title=kwargs.get('event_title'),
            description=kwargs.get('description')
        )
        event.user.add(user)
        event.outlet.add(outlet)
        event.save()
        success = ["Event created successfully!"]
        return CreateEvent(event=event, success=success)


class UpdateEvent(graphene.Mutation):
    """Mutation updates an event on a calendar.
    """
    event = graphene.Field(EventType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String(required=True)
        event_type_id = graphene.String(required=True)
        start = graphene.Date(required=True)
        end = graphene.Date(required=True)
        event_title = graphene.String(required=True)
        description = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        request_user = info.context.user
        _id = kwargs['id']
        try:
            event = Event.objects.get(id=_id)
        except Event.DoesNotExist:
            raise GraphQLError(f"Event with id {_id} does not exist!")

        event_creator = event.user.first()
        if str(request_user.email) != str(event_creator.email):
            raise GraphQLError("Can't update events that don't belong to you!")
        new_event = kwargs.items()

        for key, value in new_event:
            if key is not None:
                setattr(event, key, value)
        event.save()
        success = ["Event updated successfully!"]
        return UpdateEvent(event=event, success=success)


class DeleteEvent(graphene.Mutation):
    """Deletes an event
    """
    event = graphene.Field(EventType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String()

    @login_required
    def mutate(self, info, id):
        event = Event.objects.get(pk=id)
        request_user = info.context.user
        event_creator = event.user.first()
        if request_user != event_creator:
            raise GraphQLError("You can't delete events that don't belong to \
you!")
        event.delete()
        success = ["Event deleted successfully!"]

        return DeleteEvent(
            success=success
        )


class CreateEventType(graphene.Mutation):
    '''Mutation to create an event type
    '''
    event_type = graphene.Field(EventsTypeType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)

    @login_required
    @master_admin_required
    def mutate(self, info, name):
        try:
            events_type = EventTypeModel.objects.get(name=name)
            raise GraphQLError('This event type already exists!')
        except EventTypeModel.DoesNotExist:
            events_type = EventTypeModel.objects.create(name=name)
            events_type.save()
            success = ['Event Type created successfully!']
            return CreateEventType(success=success, event_type=events_type)


class Mutation(graphene.ObjectType):
    create_event = CreateEvent.Field()
    delete_event = DeleteEvent.Field()
    update_event = UpdateEvent.Field()
    create_event_type = CreateEventType.Field()
