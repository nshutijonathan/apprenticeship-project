import graphene
from graphene.utils.resolve_only_args import resolve_only_args
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.utils.orders_utils import operations_or_master_admin_required


class SuppliersType(DjangoObjectType):
    class Meta:
        model = Suppliers
        filter_fields = {
            'city__name': ['exact', 'icontains', 'istartswith'],
            'tier__name': ['exact', 'icontains', 'istartswith'],
            'payment_terms__name': ['exact', 'icontains', 'istartswith'],
            'credit_days': ['exact'],
            'rating': ['exact']
        }
        interfaces = (graphene.relay.Node, )
    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class Query(graphene.AbstractType):
    all_suppliers = graphene.List(SuppliersType)
    edit_requests = graphene.List(SuppliersType)
    approved_suppliers = graphene.List(SuppliersType)
    filter_suppliers = DjangoFilterConnectionField(SuppliersType)

    @operations_or_master_admin_required
    def resolve_all_suppliers(self, info):
        return Suppliers.objects.filter(parent=None)

    @operations_or_master_admin_required
    def resolve_edit_requests(self, info):
        return Suppliers.objects.exclude(parent=None)

    @login_required
    def resolve_approved_suppliers(self, info):
        return Suppliers.objects.filter(is_approved=True)

    @login_required
    def resolve_filter_suppliers(self, info, **kwargs):
        supplier = Suppliers.objects.filter(**kwargs, parent=None)

        for key in kwargs:
            if kwargs[key] == "":
                message = 'Please provide a valid search keyword'
                raise GraphQLError(message)

        if not supplier:
            message = "Supplier matching query does not exist!"
            raise GraphQLError(message)

        return supplier
