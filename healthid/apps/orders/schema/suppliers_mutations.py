import graphene
from django.forms.models import model_to_dict
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.utils.orders_utils import (EditSupplierManager,
                                         SuppliersContextManager, add_supplier,
                                         operations_or_master_admin_required)

from .suppliers_query import SuppliersType


class SuppliersInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String()
    mobile_number = graphene.String()
    address_line_1 = graphene.String()
    address_line_2 = graphene.String()
    lga = graphene.String()
    city_id = graphene.Int()
    tier_id = graphene.Int()
    rating = graphene.Int()
    credit_days = graphene.Int()
    logo = graphene.String()
    payment_terms_id = graphene.Int()
    commentary = graphene.String()


class AddSupplier(graphene.Mutation):
    class Arguments:
        input = SuppliersInput(required=True)

    supplier = graphene.Field(SuppliersType)

    @classmethod
    @login_required
    def mutate(cls, root, info, input=None):
        supplier = Suppliers()
        user = info.context.user
        add_supplier.create_supplier(user, supplier, input)
        return cls(supplier=supplier)


class ApproveSupplier(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    success = graphene.Field(graphene.String)

    @classmethod
    @operations_or_master_admin_required
    def mutate(cls, root, info, id):
        with SuppliersContextManager(id) as supplier:
            supplier.is_approved = True
            name = supplier.name
            supplier.save()
            success = f"supplier {name} has been approved!"
            return cls(success=success)


class DeleteSupplier(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    success = graphene.Field(graphene.String)

    @classmethod
    @operations_or_master_admin_required
    def mutate(cls, root, info, id):
        with SuppliersContextManager(id=id) as supplier:
            name = supplier.name
            supplier.delete()
            success = f"Supplier {name} has been deleted!"
            return cls(success=success)


class EditSupplier(graphene.Mutation):
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
        rating = graphene.Int()
        credit_days = graphene.Int()
        logo = graphene.String()
        payment_terms_id = graphene.Int()
        commentary = graphene.String()
    edit_request = graphene.Field(SuppliersType)
    message = graphene.Field(graphene.String)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        with SuppliersContextManager(kwargs.get('id')) as supplier:
            if kwargs.get('email') is not None:
                email = kwargs.get('email')
            else:
                email = supplier.email
            with EditSupplierManager(email) as edit_request:
                kwargs.pop('id')
                for (key, value) in kwargs.items():
                    if key is not None:
                        setattr(edit_request, key, value)
                edit_request.user = info.context.user
                edit_request.parent = supplier
                edit_request.save()
                name = supplier.name
                msg = f"Edit request for Supplier {name} has been sent!"
                return cls(edit_request, msg)


class ApproveEditRequest(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    message = graphene.Field(graphene.String)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @operations_or_master_admin_required
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        request_instance = Suppliers.objects.get(id=id)
        dict_object = model_to_dict(request_instance)
        parent_id = dict_object.get('parent')
        pop_list = \
            ['supplier_id', 'parent', 'user', 'is_approved', 'admin_comment']
        [dict_object.pop(key) for key in pop_list]
        dict_object['city_id'] = dict_object.pop('city')
        dict_object['tier_id'] = dict_object.pop('tier')
        dict_object['payment_terms_id'] = dict_object.pop('payment_terms')
        with SuppliersContextManager(parent_id) as supplier:
            name = supplier.name
            for (key, value) in dict_object.items():
                if value is not None:
                    setattr(supplier, key, value)
            request_instance.delete()
            supplier.save()
            message = f"Supplier {name} has been successfully updated!"
            return cls(message, supplier)


class DeclineEditRequest(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        comment = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    edit_request = graphene.Field(SuppliersType)

    @classmethod
    @operations_or_master_admin_required
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        comment = kwargs.get('comment')
        edit_request = Suppliers.objects.get(id=id)
        edit_request.admin_comment = comment
        edit_request.save()
        supplier_name = edit_request.name
        msg = f"Edit request for supplier {supplier_name} has been declined!"
        return cls(msg, edit_request)


class Mutation(graphene.ObjectType):
    add_supplier = AddSupplier.Field()
    approve_supplier = ApproveSupplier.Field()
    delete_supplier = DeleteSupplier.Field()
    edit_supplier = EditSupplier.Field()
    approve_edit_request = ApproveEditRequest.Field()
    decline_edit_request = DeclineEditRequest.Field()
