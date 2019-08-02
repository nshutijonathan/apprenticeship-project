import graphene
from graphene_django import DjangoObjectType

from healthid.apps.consultation.models import (
    ConsultationCatalogue, CustomerConsultation)


class ConsultantType(DjangoObjectType):
    class Meta:
        model = ConsultationCatalogue


class ScheduleType(DjangoObjectType):
    class Meta:
        model = CustomerConsultation


class Query(graphene.ObjectType):
    pass
