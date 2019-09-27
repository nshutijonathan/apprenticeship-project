import graphene
from django.forms.models import model_to_dict
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers, SupplierNote
from healthid.apps.outlets.models import Outlet
from healthid.apps.orders.schema.suppliers_query import (SuppliersType,
                                                         SupplierNoteType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.validators import special_cahracter_validation
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import\
    ORDERS_ERROR_RESPONSES, ORDERS_SUCCESS_RESPONSES


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
    """
    Add a new supplier to the database

    args:
        name(str): supplier name
        email(str): supplier contact email
        mobile_number(str): contact number
        address_line_1(str): first address line
        address_line_2(str): second address line
        lga(str): name of the supplier's local goverment area
        city_id(int): id of the supplier city location
        tier_id(int): id of the supplier's category
        rating(int): supplier rating
        credit_days(int): average number of days expected to settle outstanding
                          payments to the supplier
        logo(str): image URL for the supplier logo
        payment_terms_id(int): id of the preferred payment method
        commentary(str): additional comments

    returns:
        supplier(obj): 'Suppliers' model object detailing the created supplier.
    """

    class Arguments:
        input = SuppliersInput(required=True)

    supplier = graphene.Field(SuppliersType)

    @classmethod
    @login_required
    def mutate(cls, root, info, input=None):
        user = info.context.user
        supplier = Suppliers()
        for (key, value) in input.items():
            setattr(supplier, key, value)
        supplier.user = user
        with SaveContextManager(supplier, model=Suppliers) as supplier:
            return cls(supplier=supplier)


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


class DeleteSupplier(graphene.Mutation):
    """
    Delete a supplier

    args:
        id(str): id of the supplier to be deleted

    returns:
        success(str): success message confirming deleted supplier
    """

    class Arguments:
        id = graphene.String(required=True)
    success = graphene.Field(graphene.String)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, id):
        supplier = get_model_object(Suppliers, 'id', id)
        name = supplier.name
        supplier.delete()
        success = SUCCESS_RESPONSES[
            "deletion_success"].format("Supplier" + name)
        return cls(success=success)


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
        rating(int): supplier rating
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


class EditProposal(graphene.Mutation):
    """
    Edit a proposed supplier's details

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
        rating(int): supplier rating
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
        id = kwargs.get('id')
        proposed_edit = get_model_object(Suppliers, 'id', id)
        if proposed_edit.user != info.context.user:
            msg = ORDERS_ERROR_RESPONSES["edit_proposal_validation_error"]
            raise GraphQLError(msg)
        kwargs.pop('id')
        for (key, value) in kwargs.items():
            if key is not None:
                setattr(proposed_edit, key, value)
        params = {'model': Suppliers}
        with SaveContextManager(proposed_edit, **params) as edit_request:
            name = proposed_edit.parent.name
            msg = SUCCESS_RESPONSES["update_success"].format("Supplier" + name)
            return cls(edit_request, msg)


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


class CreateSupplierNote(graphene.Mutation):
    """
    Create a note for a particular supplier

    args:
        supplier_id(str): id of the supplier of note
        outlet_ids(list): outlets that source products from the supplier
        note(str): note to create for the supplier

    returns:
        message(str): success message confirming note creation
        supplier_note(obj): 'SupplierNote' model object detailing the
                            created note
        supplier(obj): 'Suppliers' model object detailing the noted supplier
    """

    class Arguments:
        supplier_id = graphene.String(required=True)
        outlet_ids = graphene.List(graphene.Int, required=True)
        note = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    supplier_note = graphene.Field(SupplierNoteType)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        supplier_id = kwargs.get("supplier_id")
        user = info.context.user
        outlet_ids = kwargs.get("outlet_ids")
        note = kwargs.get("note")
        special_cahracter_validation(note)
        if len(note.split()) < 2:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES["supplier_note_length_error"])
        supplier = get_model_object(Suppliers, "id", supplier_id)
        outlets = [get_model_object(Outlet, 'id', outlet_id)
                   for outlet_id in outlet_ids]
        supplier_note = SupplierNote(supplier=supplier, note=note, user=user)
        with SaveContextManager(supplier_note) as supplier_note:
            supplier_note.outlet.add(*outlets)
            supplier_note.save()
            return cls(
                supplier_note=supplier_note,
                supplier=supplier,
                message=SUCCESS_RESPONSES[
                    "creation_success"].format("Supplier's note"))


class UpdateSupplierNote(graphene.Mutation):
    """
    Update a supplier note

    args:
        supplier_id(str): id of the supplier of note
        outlet_ids(list): outlets that source products from the supplier
        note(str): text to update supplier note with

    returns:
        success(str): success message confirming note update
        supplier_note(obj): 'SupplierNote' model object detailing the
                            updated note
    """

    class Arguments:
        id = graphene.Int(required=True)
        supplier_id = graphene.String()
        outlet_ids = graphene.List(graphene.Int)
        note = graphene.String()
    success = graphene.Field(graphene.String)
    supplier_note = graphene.Field(SupplierNoteType)

    @classmethod
    @login_required
    @user_permission('Operations Admin')
    def mutate(cls, root, info, id, **kwargs):
        outlet_ids = kwargs.pop('outlet_ids')
        supplier_note = get_model_object(SupplierNote, "id", id)
        if info.context.user != supplier_note.user:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES[
                    "supplier_note_update_validation_error"])
        for key, value in kwargs.items():
            if key in ["note"]:
                special_cahracter_validation(value)
                if len(value.split()) < 2:
                    raise GraphQLError(
                        ORDERS_ERROR_RESPONSES["supplier_note_length_error"])
            setattr(supplier_note, key, value)

        if outlet_ids:
            outlets = [get_model_object(Outlet, 'id', outlet_id)
                       for outlet_id in outlet_ids]
            supplier_note.outlet.clear()
            supplier_note.outlet.add(*outlets)
        with SaveContextManager(supplier_note) as supplier_note:
            return cls(
                success=SUCCESS_RESPONSES[
                    "update_success"].format("Supplier's note"),
                supplier_note=supplier_note)


class DeleteSupplierNote(graphene.Mutation):
    """
    Delete a supplier note

    args:
        id(int): id of the note to delete

    returns:
        success(str): success message confirming note delete
        id(int)): id of the deleted note
    """

    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, id):
        user = info.context.user
        supplier_note = get_model_object(SupplierNote, "id", id)
        if info.context.user != supplier_note.user:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES[
                    "supplier_note_deletion_validation_error"])
        supplier_note.delete(user)
        return DeleteSupplierNote(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Supplier's note"))


class Mutation(graphene.ObjectType):
    add_supplier = AddSupplier.Field()
    approve_supplier = ApproveSupplier.Field()
    delete_supplier = DeleteSupplier.Field()
    edit_supplier = EditSupplier.Field()
    edit_proposal = EditProposal.Field()
    approve_edit_request = ApproveEditRequest.Field()
    decline_edit_request = DeclineEditRequest.Field()
    create_suppliernote = CreateSupplierNote.Field()
    update_suppliernote = UpdateSupplierNote.Field()
    delete_suppliernote = DeleteSupplierNote.Field()
