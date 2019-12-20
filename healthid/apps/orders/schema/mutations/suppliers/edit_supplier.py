import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.utils.app_utils.validator import validator
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.utils.messages.orders_responses import \
    ORDERS_ERROR_RESPONSES, ORDERS_SUCCESS_RESPONSES
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier_contacts \
    import EditSupplierContacts
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier_meta \
    import EditSupplierMeta


class SuppliersContacts(graphene.InputObjectType):
    email = graphene.String()
    mobile_number = graphene.String()
    address_line_1 = graphene.String()
    address_line_2 = graphene.String()
    lga = graphene.String()
    city_id = graphene.Int()
    country_id = graphene.Int()


class SuppliersMeta(graphene.InputObjectType):
    display_name = graphene.String()
    credit_days = graphene.Int()
    logo = graphene.String()
    payment_terms = graphene.String(required=True)
    commentary = graphene.String()


class EditSupplier(graphene.Mutation):
    """
    Edit a supplier's details

    args:
        id(str): id of the supplier to be edited
        name(str): name of the supplier
        email(str): contact email
        mobile_number(str): contact number
        address_line_1(str): address line 1
        address_line_2(str): address line 2
        lga(str): lga/region name
        city_id(int): id of the city
        tier_id(int): id of the tier
        country_id(int): id of the country
        credit_days(int): credit_days
        logo(str): logo
        payment_terms(str): payment_terms
        commentary(str): commentary

    returns:
        edit_request(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit
    """

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        tier_id = graphene.Int()
        contacts = SuppliersContacts()
        meta = SuppliersMeta()

    edit_request = graphene.Field(SuppliersType)
    message = graphene.Field(graphene.String)

    @classmethod
    def validate_fields(cls, info, supplier, kwargs):
        fields = kwargs

        if fields.get('name'):
            fields['name'] = fields['name'].strip()
            fields['name'] = validator.special_character_validation(
                fields.get('name'), 'supplier name')

        if not fields.get('tier_id'):
            fields['tier_id'] = supplier.tier_id
        fields['user'] = info.context.user
        fields['parent'] = supplier
        fields['is_approved'] = True
        fields['business_id'] = supplier.business_id

        del fields['id']
        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        edit_request = Suppliers()
        id = kwargs.get('id')
        contacts = kwargs.get('contacts') or None
        meta = kwargs.get('meta') or None
        supplier = get_model_object(Suppliers, 'id', id)

        if not supplier.is_approved:
            msg = ORDERS_ERROR_RESPONSES[
                "supplier_edit_proposal_validation_error"]
            raise GraphQLError(msg)

        fields = cls.validate_fields(info, supplier, kwargs)

        for (key, value) in fields.items():
            if key is not None:
                setattr(edit_request, key, value)

        with SaveContextManager(edit_request, model=Suppliers) as edit_request:
            name = supplier.name
            msg = ORDERS_SUCCESS_RESPONSES[
                "supplier_edit_request_success"].format(name)

            if contacts:
                contacts['supplier_id'] = id
                contacts['edit_request_id'] = edit_request.id
                EditSupplierContacts.mutate(root, info, **contacts)

            if meta:
                meta['supplier_id'] = id
                meta['edit_request_id'] = edit_request.id
                EditSupplierMeta.mutate(root, info, **meta)

            return cls(edit_request, msg)
