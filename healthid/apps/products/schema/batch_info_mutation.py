from itertools import compress

import graphene
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.apps.products.schema.product_query import (BatchInfoType,
                                                         QuantityType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.validators import check_validity_of_ids
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.utils.product_utils.product import \
    generate_reorder_points_and_max
from healthid.utils.messages.products_responses import\
    PRODUCTS_ERROR_RESPONSES, PRODUCTS_SUCCESS_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class CreateBatchInfo(graphene.Mutation):
    """
        Mutation to create a Product batch Information
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        supplier_id = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        date_received = graphene.String(required=True)
        pack_size = graphene.String()
        quantity = graphene.Int(required=True)
        expiry_date = graphene.String(required=True)
        unit_cost = graphene.Float(required=True)
        commentary = graphene.String()
        user_id = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @login_required
    @batch_info_instance
    def mutate(self, info, **kwargs):
        user = info.context.user
        quantity = kwargs.pop('quantity')
        kwargs['date_received'] = parse_date(kwargs.get('date_received'))
        kwargs['expiry_date'] = parse_date(kwargs.get('expiry_date'))

        batch_info = BatchInfo(user=user)
        for key, value in kwargs.items():
            setattr(batch_info, key,  value)

        with SaveContextManager(batch_info, model=BatchInfo) as batch_info:
            quantity = Quantity(
                batch=batch_info, quantity_received=quantity,
                quantity_remaining=quantity, is_approved=True)
            quantity.save()
            generate_reorder_points_and_max(batch_info.product)
            message = SUCCESS_RESPONSES["creation_success"].format("Batch")
            return CreateBatchInfo(message=message, batch_info=batch_info)


class UpdateBatchInfo(graphene.Mutation):
    """
        Mutation to update a Product batch Information
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        batch_id = graphene.String(required=True)
        supplier_id = graphene.String()
        date_received = graphene.String()
        pack_size = graphene.String()
        expiry_date = graphene.String()
        unit_cost = graphene.Float()
        commentary = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @classmethod
    @login_required
    @batch_info_instance
    @user_permission('Manager')
    def mutate(cls, root, info, **kwargs):
        batch_id = kwargs.pop('batch_id')
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        for (key, value) in kwargs.items():
            if key is not None:
                if key in ('date_received', 'expiry_date'):
                    value = parse_date(value)
                setattr(batch_info, key, value)
        with SaveContextManager(batch_info, model=BatchInfo) as batch_info:
            message = SUCCESS_RESPONSES[
                "update_success"].format(
                    "Batch with number " + str(batch_info.batch_no))
            return UpdateBatchInfo(message=message, batch_info=batch_info)


class ProposeQuantity(graphene.Mutation):
    """
        Mutation to propose a quantity edit to a batch
    """
    batch_info = graphene.List(BatchInfoType)

    class Arguments:
        product_id = graphene.Int(required=True)
        batch_ids = graphene.List(graphene.String, required=True)
        proposed_quantities = graphene.List(graphene.Int, required=True)

    notification = graphene.String()

    @classmethod
    @login_required
    @user_permission('Manager', 'Operations Admin')
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        batch_ids = kwargs.get('batch_ids')
        product_id = kwargs.get('product_id')
        proposed_quantities = kwargs.get('proposed_quantities', None)

        unique_batches_count = len(set(batch_ids))
        if len(batch_ids) != unique_batches_count or \
                len(proposed_quantities) != unique_batches_count:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["batch_match_error"])
        product = get_model_object(Product, 'id', product_id)
        product_batches = product.get_batches(batch_ids)

        all_proposals = Quantity.get_proposed_quantities()
        pending_request_exists = [
            all_proposals.filter(batch_id=id).exists() for id in batch_ids
        ]
        if any(pending_request_exists):
            pending_proposals = list(
                compress(batch_ids, [item for item in pending_request_exists]))
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["request_approval_error"].format(
                    pending_proposals))

        for batch_id, proposed_quantity in zip(batch_ids, proposed_quantities):
            original_quantity = product.batch_info.get(
                id=batch_id).batch_quantities.get()
            edit_quantity = Quantity(
                batch_id=batch_id, parent=original_quantity, proposed_by=user,
                quantity_remaining=proposed_quantity,
                quantity_received=original_quantity.quantity_received
            )
            with SaveContextManager(edit_quantity, model=Quantity):
                pass
        notification = (PRODUCTS_SUCCESS_RESPONSES["edit_request_success"])
        return cls(batch_info=product_batches, notification=notification)


class ApproveProposedQuantity(graphene.Mutation):
    """
        Mutation to approve or decline a quantity edit to a batch
    """
    quantity_instance = graphene.List(QuantityType)

    class Arguments:
        product_id = graphene.Int(required=True)
        batch_ids = graphene.List(graphene.String, required=True)
        is_approved = graphene.Boolean(required=True)
        comment = graphene.String()

    message = graphene.String()

    @classmethod
    @login_required
    @user_permission('Operations Admin')
    def mutate(cls, root, info, **kwargs):
        approval_status = kwargs.get('is_approved')
        user = info.context.user
        batch_ids = kwargs.get('batch_ids')
        product_id = kwargs.get('product_id')
        comment = kwargs.get('comment', None)

        product = get_model_object(Product, 'id', product_id)
        product_batches = product.get_batches(batch_ids)
        batches_proposals = Quantity.get_proposed_quantities()
        batches_proposals_ids = batches_proposals.values_list(
            'batch_id', flat=True)
        message = PRODUCTS_ERROR_RESPONSES["inexistent_proposal_error"]
        check_validity_of_ids(
            batch_ids, batches_proposals_ids, message=message)

        if not approval_status and not comment:
            raise GraphQLError("Comment please")

        for batch in product_batches:
            date_batch_received = batch.date_received
            original_instance = batch.batch_quantities.get(
                parent_id__isnull=True)
            proposed_instance = batches_proposals.filter(batch=batch).first()
            if approval_status:
                original_instance.quantity_remaining = \
                    proposed_instance.quantity_remaining
                proposed_instance.is_approved = True
            else:
                proposed_instance.request_declined = True
            proposed_instance.authorized_by = user
            proposed_instance.comment = comment
            proposed_instance.save()
            original_instance.save()
            message = (PRODUCTS_SUCCESS_RESPONSES[
                "proposal_approval_success"].format(
                product, date_batch_received)
            ) if approval_status else (
                PRODUCTS_ERROR_RESPONSES[
                    "proposal_decline"].format(product, date_batch_received))

        return cls(message=message, quantity_instance=batches_proposals)


class DeleteBatchInfo(graphene.Mutation):
    """
        Delete a Product batch Info Mutation
    """

    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        batch_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    @user_permission('Manager')
    def mutate(root, info, **kwargs):
        user = info.context.user
        batch_id = kwargs.get('batch_id')
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        batch_info.delete(user)
        message = SUCCESS_RESPONSES[
            "deletion_success"].format(
            "Batch with number " + str(
                batch_info.batch_no))
        return DeleteBatchInfo(message=message)
