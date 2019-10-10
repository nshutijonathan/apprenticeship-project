import graphene

from healthid.apps.orders.models import Suppliers
from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class DeclineEditRequest(graphene.Mutation):
    """
    Decline an edit to a supplier's details

    args:
        id(str): id of the supplier to be edited

    returns:
        supplier(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit decline
    """

    class Arguments:
        id = graphene.String(required=True)
        comment = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    edit_request = graphene.Field(SuppliersType)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        comment = kwargs.get('comment')
        edit_request = Suppliers.objects.get(id=id)
        edit_request.admin_comment = comment
        edit_request.save()
        supplier_name = edit_request.name
        msg = ORDERS_ERROR_RESPONSES[
            "supplier_request_denied"].format(supplier_name)
        return cls(msg, edit_request)
