import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.db.models import Q

from healthid.apps.events.models import Event
from healthid.apps.outlets.models import Outlet
from django.shortcuts import get_object_or_404
from graphql import GraphQLError
from healthid.apps.events.models import EventType as EventTypeModel


class EventsType(DjangoObjectType):
    class Meta:
        model = Event


class EventTypeType(DjangoObjectType):

    class Meta:
        model = EventTypeModel


class Query(graphene.ObjectType):
    events = graphene.List(EventsType)
    event = graphene.Field(
        EventsType,
        id=graphene.String(),
        business=graphene.String(),
        outlet=graphene.String(),
        event_type=graphene.String(),
        event_title=graphene.String(),
        start=graphene.Date(),
        end=graphene.Date(),
        description=graphene.String()
    )
    event_types = graphene.List(EventTypeType)

    @login_required
    def resolve_events(self, info, **kwargs):
        user = info.context.user
        try:
            outlet = get_object_or_404(Outlet, user=user)
        except Outlet.DoesNotExist:
            raise GraphQLError("You can't view events if you're not attached to \
an outlet!")
        events = Event.objects.filter(Q(user=user) | Q(outlet=outlet))
        if not events:
            raise GraphQLError('No events to view yet!')
        return events

    @login_required
    def resolve_event(self, info, **kwargs):
        id = kwargs.get('id')
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            raise GraphQLError(f"Event with id {id} doesn't exist!")
        return event

    @login_required
    def resolve_event_types(self, info, **kwargs):
        return EventTypeModel.objects.all()
