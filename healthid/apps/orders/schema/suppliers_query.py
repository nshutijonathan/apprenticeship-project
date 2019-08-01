import graphene
from graphene.utils.resolve_only_args import resolve_only_args
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers, SupplierNote
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT


class SuppliersType(DjangoObjectType):
    class Meta:
        model = Suppliers
        # Specifying model fields to filter by
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
        """
        Overriding relay's global ID to return the database ID
        :return: database ID
        """
        return self.id


class SupplierNoteType(DjangoObjectType):
    class Meta:
        model = SupplierNote


class Query(graphene.AbstractType):
    """
    Query data related to the 'Suppliers' model

    args:
        id(str): supplier note id used to make the 'suppliersNote' query.
                 Returns a single supplier's note

    returns:
        all_suppliers(list): returns all suppliers in the database with a null
                             'parent' field
        edit_request(list): returns all suppliers that have a non-null
                            'parent' field
        approved_suppliers(list): returns all approved suppliers
        user_requests(list): returns suppliers created by the current user
        filter_suppliers(list): returns suppliers based on filter parameters
        all_suppliers_note(list): returns all suppliers notes
        suppliers_note(list): returns a supplier's note
    """

    all_suppliers = graphene.List(SuppliersType, page_count=graphene.Int(),
                                  page_number=graphene.Int())
    edit_requests = graphene.List(SuppliersType)
    approved_suppliers = graphene.List(SuppliersType,
                                       page_count=graphene.Int(),
                                       page_number=graphene.Int())
    user_requests = graphene.List(SuppliersType)
    filter_suppliers = DjangoFilterConnectionField(SuppliersType)
    all_suppliers_note = graphene.List(SupplierNoteType)
    suppliers_note = graphene.List(SupplierNoteType,
                                   id=graphene.String(required=True))

    @user_permission('Operations Admin')
    def resolve_all_suppliers(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        suppliers_set = Suppliers.objects.filter(parent=None)
        if page_count or page_number:
            suppliers = pagination_query(
                suppliers_set, page_count, page_number)
            return suppliers
        return pagination_query(suppliers_set,
                                PAGINATION_DEFAULT["page_count"],
                                PAGINATION_DEFAULT["page_number"])

    @user_permission('Operations Admin')
    def resolve_edit_requests(self, info):
        return Suppliers.objects.exclude(parent=None)

    @login_required
    def resolve_approved_suppliers(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        approved_suppliers_set = Suppliers.objects.filter(is_approved=True)
        if page_count or page_number:
            approved_suppliers = pagination_query(
                approved_suppliers_set, page_count, page_number)
            return approved_suppliers
        return pagination_query(approved_suppliers_set,
                                PAGINATION_DEFAULT["page_count"],
                                PAGINATION_DEFAULT["page_number"])

    @login_required
    def resolve_user_requests(self, info):
        user = info.context.user
        return Suppliers.objects.filter(user=user).exclude(parent=None)

    @login_required
    def resolve_filter_suppliers(self, info, **kwargs):
        for key in kwargs:
            if kwargs[key] == "":
                message = ORDERS_ERROR_RESPONSES["supplier_search_key_error"]
                raise GraphQLError(message)

        supplier = Suppliers.objects.filter(**kwargs, parent=None)
        if not supplier:
            message = ORDERS_ERROR_RESPONSES[
                "inexistent_supplier_search_error"]
            raise GraphQLError(message)

        return supplier

    @login_required
    def resolve_suppliers_note(self, info, **kwargs):
        id = kwargs.get('id')
        supplier = get_model_object(Suppliers, 'id', id)
        return SupplierNote.objects.filter(supplier_id=supplier)

    @login_required
    def resolve_all_suppliers_note(self, info):
        return SupplierNote.objects.all()
