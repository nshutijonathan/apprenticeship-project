from django.db.models import Avg
import graphene
from graphene.utils.resolve_only_args import resolve_only_args
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import (Suppliers,
                                         SupplierNote,
                                         Tier,
                                         PaymentTerms,
                                         SupplierRating)
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
            'country__name': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
            'is_approved': ['exact']
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


class TierType(DjangoObjectType):
    class Meta:
        model = Tier


class PaymentTermsType(DjangoObjectType):
    class Meta:
        model = PaymentTerms


class SupplierRatingType(DjangoObjectType):
    class Meta:
        model = SupplierRating


class Query(graphene.AbstractType):
    """
    Query data related to the 'Suppliers' model

    args:
        id(str): supplier note id used to make the 'suppliersNote' query.
                 Returns a single supplier's note

    returns:
        all_suppliers(list): returns all suppliers in the database with a null
                             'parent' field
        single_supplier(field): returns a particular supplier by id or name
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
    single_supplier = graphene.Field(SuppliersType,
                                     name=graphene.String(),
                                     id=graphene.String())
    edit_requests = graphene.List(SuppliersType)
    approved_suppliers = graphene.List(SuppliersType,
                                       page_count=graphene.Int(),
                                       page_number=graphene.Int())
    user_requests = graphene.List(SuppliersType)
    filter_suppliers = DjangoFilterConnectionField(SuppliersType)
    all_suppliers_note = graphene.List(SupplierNoteType,
                                       page_count=graphene.Int(),
                                       page_number=graphene.Int())
    suppliers_note = graphene.List(SupplierNoteType,
                                   id=graphene.String(required=True))
    total_suppliers_pages_count = graphene.Int()
    pagination_result = None

    supplier_rating = graphene.Float(
        supplier_id=graphene.String(required=True))

    @user_permission('Operations Admin')
    def resolve_all_suppliers(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user_id = info.context.user.id
        suppliers_set = Suppliers.objects.filter(
            user_id=user_id).order_by('id')
        if page_count or page_number:
            suppliers = pagination_query(
                suppliers_set, page_count, page_number)
            Query.pagination_result = suppliers
            return suppliers[0]
        paginated_response = pagination_query(suppliers_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_single_supplier(self, info, **kwargs):
        name = kwargs.get('name')
        id = kwargs.get('id')
        if not (name or id):
            message = ORDERS_ERROR_RESPONSES[
                "invalid_supplier_field"]
            raise GraphQLError(message)
        field, value = ('id', id) if id else('name', name)
        supplier = get_model_object(Suppliers, field, value)
        return supplier

    @user_permission('Operations Admin')
    def resolve_edit_requests(self, info):
        return Suppliers.objects.exclude(parent=None)

    @login_required
    def resolve_total_suppliers_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying, totalSuppliersPagesCount query field should
        strictly be called after the suppliers query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_approved_suppliers(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        approved_suppliers_set = Suppliers.objects.filter(
            is_approved=True
        ).order_by('id')
        if page_count or page_number:
            approved_suppliers = pagination_query(
                approved_suppliers_set, page_count, page_number)
            Query.pagination_result = approved_suppliers
            return approved_suppliers[0]
        paginated_response = pagination_query(approved_suppliers_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

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

            kwargs[key] = kwargs[key].strip() \
                if key == "name__icontains" else kwargs[key]

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
    def resolve_all_suppliers_note(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        suppliers_notes_set = SupplierNote.objects.all().order_by('id')
        if page_count or page_number:
            suppliers_notes = pagination_query(
                suppliers_notes_set, page_count, page_number)
            Query.pagination_result = suppliers_notes
            return suppliers_notes[0]
        paginated_response = pagination_query(suppliers_notes_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_supplier_rating(self, info, **kwargs):
        supplier_id = kwargs.get("supplier_id")
        rating = SupplierRating.objects.filter(
            supplier_id=supplier_id).aggregate(Avg('rating'))
        try:
            return round(rating['rating__avg'], 1)
        except TypeError:
            return 0
