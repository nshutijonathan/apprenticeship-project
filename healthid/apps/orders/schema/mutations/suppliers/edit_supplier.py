import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.utils.messages.orders_responses import \
    ORDERS_ERROR_RESPONSES, ORDERS_SUCCESS_RESPONSES


class EditSupplier(graphene.Mutation):
    """
    Edit a supplier's details

    args:
        id(str): id of the supplier to be edited
        name(str): supplier name
        email(str): supplier contact email
        mobile_number(str): contact number
        address_line_1(str): first address line
        address_line_2(str): second address line
        lga(str): name of the supplier's local goverment area
        city_id(int): id of the supplier city location
        tier_id(int): id of the supplier's category
        country_id(int): supplier country
        credit_days(int): average number of days expected to settle outstanding
                          payments to the supplier
        logo(str): image URL for the supplier logo
        payment_terms_id(int): id of the preferred payment method
        commentary(str): additional comments

    returns:
        edit_request(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit
    """

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        email = graphene.String()
        mobile_number = graphene.String()
        address_line_1 = graphene.String()
        address_line_2 = graphene.String()
        lga = graphene.String()
        city_id = graphene.Int()
        tier_id = graphene.Int()
        country_id = graphene.Int()
        credit_days = graphene.Int()
        logo = graphene.String()
        payment_terms_id = graphene.Int()
        commentary = graphene.String()

    edit_request = graphene.Field(SuppliersType)
    message = graphene.Field(graphene.String)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        edit_request = Suppliers()
        supplier = get_model_object(Suppliers, 'id', id)
        if not supplier.is_approved:
            msg = ORDERS_ERROR_RESPONSES[
                "supplier_edit_proposal_validation_error"]
            raise GraphQLError(msg)

        kwargs.pop('id')
        for (key, value) in kwargs.items():
            if key is not None:
                setattr(edit_request, key, value)
        if not kwargs.get('city_id'):
            edit_request.city_id = supplier.city_id
        if not kwargs.get('payment_terms_id'):
            edit_request.payment_terms_id = \
                supplier.payment_terms_id
        if not kwargs.get('tier_id'):
            edit_request.tier_id = supplier.tier_id
        edit_request.user = info.context.user
        edit_request.parent = supplier
        edit_request.is_approved = True
        with SaveContextManager(edit_request, model=Suppliers) as edit_request:
            name = supplier.name
            msg = ORDERS_SUCCESS_RESPONSES[
                "supplier_edit_request_success"].format(name)
            return cls(edit_request, msg)
