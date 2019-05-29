from functools import reduce

import graphene
from django.db.models import Q
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.apps.products.schema.product_query import (BatchInfoType,
                                                         QuantityType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import (batch_info_instance,
                                                      check_validity_of_ids)
from healthid.utils.product_utils.product import \
    generate_reorder_points_and_max


class CreateBatchInfo(graphene.Mutation):
    """
        Mutation to create a Product batch Information
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        supplier_id = graphene.String(required=True)
        product = graphene.List(graphene.Int, required=True)
        date_received = graphene.String()
        pack_size = graphene.String()
        quantities = graphene.List(graphene.Int, required=True)
        expiry_date = graphene.String()
        unit_cost = graphene.Float(required=True)
        commentary = graphene.String()
        outlet_id = graphene.String()
        user_id = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @batch_info_instance
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet = get_model_object(Outlet, 'user', user)
        supplier_id = kwargs.get('supplier_id')
        products = kwargs.get('product')
        quantities = kwargs.get('quantities')

        supplier_instance = get_model_object(Suppliers, 'supplier_id',
                                             supplier_id)
        if len(products) != len(quantities):
            raise GraphQLError("the number of products and quantities "
                               "provided do not match")
        batch_info = BatchInfo.objects.create(
            date_received=parse_date(kwargs.get('date_received')),
            pack_size=kwargs.get('pack_size'),
            expiry_date=parse_date(kwargs.get('expiry_date')),
            unit_cost=kwargs.get('unit_cost'),
            commentary=kwargs.get('commentary'),
            supplier=supplier_instance,
            outlet=outlet,
            user=user)
        for index, product_id in enumerate(products):
            product_instance = get_model_object(Product, 'id', product_id)
            generate_reorder_points_and_max(product_instance)
            batch_info.product.add(product_instance)
            Quantity.objects.create(
                batch=batch_info, quantity_received=quantities[index],
                product=product_instance)
            batch_info.save()
        message = ['Batch successfully created']
        return CreateBatchInfo(message=message, batch_info=batch_info)


class UpdateBatchInfo(graphene.Mutation):
    """
        Mutation to update a Product batch Information
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        batch_id = graphene.String(required=True)
        supplier_id = graphene.String()
        product = graphene.List(graphene.Int)
        date_received = graphene.String()
        pack_size = graphene.String()
        expiry_date = graphene.String()
        unit_cost = graphene.Float()
        commentary = graphene.String()
        outlet_id = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @classmethod
    @login_required
    @batch_info_instance
    @user_permission('Manager')
    def mutate(cls, root, info, **kwargs):
        batch_id = kwargs.get('batch_id')
        products = kwargs.get('product')
        supplier_id = kwargs.get('supplier_id')
        outlet_id = kwargs.get('outlet_id')
        batch_info = get_model_object(BatchInfo, 'id', batch_id)

        if products:
            batch_info.product.clear()
            for product_id in products:
                product_instance = get_model_object(Product, 'id', product_id)
                generate_reorder_points_and_max(product_instance)
                batch_info.product.add(product_instance)
        if outlet_id:
            outlet_instance = get_model_object(Outlet, 'id', outlet_id)
            batch_info.outlet = outlet_instance
        if supplier_id:
            supplier_instance = get_model_object(Suppliers, 'supplier_id',
                                                 supplier_id)
            batch_info.supplier = supplier_instance
        for (key, value) in kwargs.items():
            if key is not None:
                if key in ('batch_id', 'supplier_id', 'product'):
                    continue
                if key in ('date_received', 'expiry_date'):
                    value = parse_date(value)
                setattr(batch_info, key, value)
        batch_info.save()
        message = [
            f'Batch with number {batch_info.batch_no} '
            f'successfully updated'
        ]

        return UpdateBatchInfo(message=message, batch_info=batch_info)


class ProposeQuantity(graphene.Mutation):
    """
        Mutation to propose a quantity edit to a batch
    """
    batch_info = graphene.Field(BatchInfoType)

    class Arguments:
        batch_id = graphene.String(required=True)
        product = graphene.List(graphene.Int)
        proposed_quantities = graphene.List(graphene.Int, required=True)

    notification = graphene.String()

    @classmethod
    @login_required
    @batch_info_instance
    @user_permission('Manager', 'Operations Admin')
    def mutate(cls, root, info, **kwargs):
        batch_id = kwargs.get('batch_id')
        products = kwargs.get('product')
        proposed_quantities = kwargs.get('proposed_quantities', None)
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        query = reduce(lambda q, id: q | Q(product_id=id), products, Q())
        batch_quantities = batch_info.batch_quantities.filter(query)
        batch_products = batch_info.product.all().values_list('id', flat=True)
        check_validity_of_ids(products, batch_products)

        for batch_quantity in batch_quantities:
            if Quantity.objects.filter(parent_id=batch_quantity.id):
                raise GraphQLError("Pending request has not yet been approved")

        if len(products) != len(proposed_quantities):
            raise GraphQLError(
                "The number of products and quantities provided do not match")

        for index, value in enumerate(products):
            edit_quantity = Quantity()
            params = {
                'model_name': 'Quantity',
                'field': 'quantity_received',
                'value': proposed_quantities[index]
            }
            quantity = Quantity.objects.get(
                batch_id=batch_id, product_id=value)
            edit_quantity.parent = quantity
            edit_quantity.batch = batch_info
            edit_quantity.product_id = value
            edit_quantity.proposed_by = info.context.user
            edit_quantity.quantity_received = proposed_quantities[index]

            with SaveContextManager(edit_quantity, **params):
                pass
        notification = ("Edit request for quantity has been sent!")
        return cls(batch_info=batch_info, notification=notification)


class ApproveProposedQuantity(graphene.Mutation):
    """
        Mutation to approve or decline a quantity edit to a batch
    """
    quantity_instance = graphene.List(QuantityType)

    class Arguments:
        batch_id = graphene.String(required=True)
        product = graphene.List(graphene.Int)
        is_approved = graphene.Boolean()
        comment = graphene.String()

    message = graphene.String()

    @classmethod
    @login_required
    @user_permission('Operations Admin')
    def mutate(cls, root, info, **kwargs):
        approval_status = kwargs.get('is_approved')
        batch_id = kwargs.get('batch_id')
        product_ids = kwargs.get('product')
        comment = kwargs.get('comment')
        batch = get_model_object(BatchInfo, 'id', batch_id)
        query = reduce(lambda q, id: q | Q(product_id=id), product_ids, Q())
        quantities = batch.batch_quantities.filter(
            parent_id__isnull=False).filter(query)
        quantity_ids = quantities.values_list('product_id', flat=True)
        message = "Proposal for product with ids {} doesn't exist"
        check_validity_of_ids(product_ids, quantity_ids, message=message)

        if not approval_status and not comment:
            raise GraphQLError("Comment please")

        for quantity in quantities:
            original_instance = get_model_object(
                Quantity, 'id', quantity.parent_id)
            original_instance.quantity_received = quantity.quantity_received \
                if approval_status else original_instance.quantity_received
            original_instance.is_approved = True if approval_status else False
            original_instance.authorized_by = info.context.user
            original_instance.comment = comment if not approval_status \
                else None
            original_instance.save()
            quantity.delete()

        message = (
            "Products with ids '{}' have been successfully approved".format(
                ",".join(map(str, product_ids)))
        ) if approval_status else (
            "Proposal for quantity with ids '{}' has been"
            " declined".format(",".join(map(str, product_ids))))

        return cls(message=message, quantity_instance=quantities)


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
        batch_id = kwargs.get('batch_id')
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        batch_info.delete()
        message = [f"Batch with number {batch_info.batch_no} has been deleted"]
        return DeleteBatchInfo(message=message)
