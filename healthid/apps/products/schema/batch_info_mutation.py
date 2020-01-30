from itertools import compress
from re import sub
import graphene
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from graphql.language import ast
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
from healthid.utils.messages.products_responses import \
    PRODUCTS_ERROR_RESPONSES, PRODUCTS_SUCCESS_RESPONSES
from healthid.utils.messages.common_responses import \
    SUCCESS_RESPONSES, ERROR_RESPONSES


class ServiceQuality(graphene.types.Scalar):
    """
    Custom type for service Quality rating (integer, range: 1 - 5)
    """
    @staticmethod
    def enforce_int_range(value):
        if isinstance(value, int) and 1 <= value <= 5:
            return value
        raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])

    parse_value = enforce_int_range
    serialize = enforce_int_range

    @staticmethod
    def parse_literal(node):
        try:
            value = int(node.value)
            if isinstance(node, ast.IntValue) and 1 <= value <= 5:
                return value
            raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])
        except ValueError:
            raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])


class CreateBatchInfo(graphene.Mutation):
    """
    Mutation to create a new product batch information

    arguments:
        supplier_id(str): id of product supplier
        date_received(str): datte order was received
        product_id(int): id of product to create batch for
        unit_cost(float): id of the product in stock
        quantity(int): quantiy of product received
        expiry_date(str): product expiry date
        service_quality(int): quality rating for supplier delivery (int, 1 - 5)
        delivery_promptness(bool): promptness of product delivery
            (true if delivery 'on time')
        comment(str): extra notes to attach to batch

    returns:
        message(str): success message confirming batch update creation
        batch_info(obj): newly created batch_info details
    """

    batch_info = graphene.Field(BatchInfoType)
    message = graphene.String()

    class Arguments:
        batch_no = graphene.String()
        supplier_id = graphene.String(required=True)
        date_received = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        unit_cost = graphene.Float(required=True)
        quantity = graphene.Int(required=True)
        expiry_date = graphene.String(required=True)
        service_quality = graphene.Argument(ServiceQuality, required=True)
        delivery_promptness = graphene.Boolean(required=True)
        comment = graphene.String()

    @login_required
    @batch_info_instance
    def mutate(self, info, **kwargs):
        user = info.context.user
        batch_n = kwargs.get('batch_no')
        quantity = kwargs.pop('quantity')
        kwargs['date_received'] = parse_date(kwargs.get('date_received'))
        kwargs['expiry_date'] = parse_date(kwargs.get('expiry_date'))
        datetime_str = sub('[-]', '', str(kwargs['date_received']))
        batch_no_auto = f'BN{datetime_str}'
        batch_info = BatchInfo(user=user)
        if not batch_n:
            kwargs['batch_no'] = batch_no_auto
        batch_ = BatchInfo.objects.filter(batch_no=kwargs.get('batch_no'))
        batch__l = list(
            map(lambda batch__: batch__.quantity == quantity, batch_))
        if True in batch__l:
            raise GraphQLError(ERROR_RESPONSES[
                'batch_exist'].format(kwargs['batch_no']))
        for key, value in kwargs.items():
            setattr(batch_info, key, value)

        with SaveContextManager(batch_info, model=BatchInfo) as batch_info:
            quantity = Quantity(
                batch=batch_info, quantity_received=quantity,
                quantity_remaining=quantity, is_approved=True)
            quantity.save()
            product = batch_info.product
            generate_reorder_points_and_max(product)
            if product.nearest_expiry_date is None or \
                    product.nearest_expiry_date > product.expiry_date:
                product.nearest_expiry_date = batch_info.expiry_date
                product.save()
            message = SUCCESS_RESPONSES["creation_success"].format("Batch")
            return CreateBatchInfo(message=message, batch_info=batch_info)


class UpdateBatchInfo(graphene.Mutation):
    """
    Mutation to update a existing product batch information

    arguments:
        batch_id(str): id of batch to update
        supplier_id(str): id of product supplier
        date_received(str): datte order was received
        unit_cost(float): id of the product in stock
        expiry_date(str): product expiry date
        service_quality(int): quality rating for supplier delivery (int, 1 - 5)
        delivery_promptness(bool): promptness of product delivery
            (true if delivery 'on time')
        comment(str): extra notes to attach to batch

    returns:
        message(str): success message confirming batch update creation
        batch_info(obj): newly created batch_info details
    """
    batch_info = graphene.Field(BatchInfoType)
    message = graphene.String()

    class Arguments:
        batch_id = graphene.String(required=True)
        supplier_id = graphene.String()
        date_received = graphene.String()
        unit_cost = graphene.Float()
        expiry_date = graphene.String()
        service_quality = graphene.Argument(ServiceQuality)
        delivery_promptness = graphene.Boolean()
        comment = graphene.String()

    @login_required
    @batch_info_instance
    @user_permission('Manager')
    def mutate(self, info, batch_id, **kwargs):
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
