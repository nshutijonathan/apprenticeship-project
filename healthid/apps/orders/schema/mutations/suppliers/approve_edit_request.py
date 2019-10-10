import graphene
from django.forms.models import model_to_dict

from healthid.apps.orders.models import Suppliers
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class ApproveEditRequest(graphene.Mutation):
    """
    Approve an edit to a supplier's details

    args:
        id(str): id of the supplier to be edited

    returns:
        supplier(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit approval
    """

    class Arguments:
        id = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        request_instance = get_model_object(Suppliers, 'id', id)
        dict_object = model_to_dict(request_instance)
        parent_id = dict_object.get('parent')
        pop_list = \
            ['supplier_id', 'parent', 'is_approved', 'admin_comment', 'outlet']
        [dict_object.pop(key) for key in pop_list]
        dict_object['user_id'] = dict_object.pop('user')
        dict_object['city_id'] = dict_object.pop('city')
        dict_object['tier_id'] = dict_object.pop('tier')
        dict_object['payment_terms_id'] = dict_object.pop('payment_terms')
        supplier = get_model_object(Suppliers, 'id', parent_id)
        name = supplier.name
        for (key, value) in dict_object.items():
            if value is not None:
                setattr(supplier, key, value)
        request_instance.hard_delete()
        supplier.save()
        message = SUCCESS_RESPONSES["update_success"].format("Supplier" + name)
        return cls(message, supplier)
