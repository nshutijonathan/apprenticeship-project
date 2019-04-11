import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.business.models import Business
from healthid.utils.auth_utils.decorator import master_admin_required


class BusinessType(DjangoObjectType):
    class Meta:
        model = Business


class Query(graphene.ObjectType):
    businesses = graphene.List(BusinessType)
    business = graphene.Field(
        BusinessType,
        id=graphene.String(),
        trading_name=graphene.String(),
        legal_name=graphene.String(),
        primary_address=graphene.String(),
        primary_phone_number=graphene.String(),
        email=graphene.String(),
        website=graphene.String(),
        facebook=graphene.String(),
        twitter=graphene.String(),
        instagram=graphene.String(),
        logo=graphene.String(),
        date_created=graphene.String(),
        user=graphene.String()
    )

    @login_required
    @master_admin_required
    def resolve_businesses(self, info, **kwargs):
        return Business.objects.all()

    @login_required
    @master_admin_required
    def resolve_business(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Business.objects.get(pk=id)
        return None
