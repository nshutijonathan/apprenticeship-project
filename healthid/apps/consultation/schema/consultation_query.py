import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.consultation.models import Consultation
from healthid.utils.app_utils.database import get_model_object


class ConsultantType(DjangoObjectType):
    class Meta:
        model = Consultation


class Query(graphene.ObjectType):
    consultations = graphene.List(ConsultantType)
    consultation = graphene.Field(
        ConsultantType,
        id=graphene.Int(),
        consultation_name=graphene.String(),
        description=graphene.String(),
        price_per_session=graphene.Int())

    @login_required
    def resolve_consultations(self, info, **kwargs):
        return Consultation.objects.all()

    @login_required
    def resolve_consultation(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return get_model_object(Consultation, 'id', id)
        return None
