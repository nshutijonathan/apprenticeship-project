import graphene

from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.apps.orders.models import Suppliers
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class ApproveSupplier(graphene.Mutation):
    """
    Approve a new supplier

    args:
        id(str): id of the supplier to be approved

    returns:
        supplier(obj): 'Suppliers' model object detailing the approved
                       supplier.
        success(str): success message confirming approved supplier
    """

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Field(graphene.String)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, id):
        supplier = get_model_object(Suppliers, 'id', id)
        supplier.is_approved = True
        name = supplier.name
        supplier.save()
        success = SUCCESS_RESPONSES[
            "approval_success"].format("Supplier" + name)
        return cls(success=success, supplier=supplier)
