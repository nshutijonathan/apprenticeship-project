import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers

from .suppliers_mutations import SuppliersType


class Query(graphene.AbstractType):
    suppliers = graphene.List(SuppliersType)

    @login_required
    def resolve_suppliers(self, info):
        return Suppliers.objects.all()
