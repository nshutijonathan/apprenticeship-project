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


class EditSupplier(graphene.Mutation):
    """
    Edit a supplier's details

    args:
        id(str): id of the supplier to be edited
        name(str): supplier name
        tier_id(int): id of the supplier's category

    returns:
        edit_request(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit
    """

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String(required=True)
        tier_id = graphene.Int()

    edit_request = graphene.Field(SuppliersType)
    message = graphene.Field(graphene.String)

    @classmethod
    def validate_fields(cls, info, supplier, kwargs):
        fields = kwargs

        if fields.get('name'):
            fields['name'] = validator.special_character_validation(
                fields.get('name'), 'supplier name')

        if not fields.get('tier_id'):
            fields['tier_id'] = supplier.tier_id
        fields['user'] = info.context.user
        fields['parent'] = supplier
        fields['is_approved'] = True

        del fields['id']
        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        edit_request = Suppliers()
        id = kwargs.get('id')
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
            return cls(edit_request, msg)
