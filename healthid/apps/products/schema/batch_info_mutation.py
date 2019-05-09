import graphene
from django.utils.dateparse import parse_date
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import BatchInfo, Product
from healthid.apps.products.schema.product_query import BatchInfoType
from healthid.utils.app_utils.database import (get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.apps.outlets.models import Outlet


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
        quantity_received = graphene.Int(required=True)
        expiry_date = graphene.String()
        unit_cost = graphene.Float(required=True)
        commentary = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @batch_info_instance
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet = get_model_object(Outlet, 'user', user)
        supplier_id = kwargs.get('supplier_id')
        products = kwargs.get('product')
        supplier_instance = get_model_object(
            Suppliers, 'supplier_id', supplier_id)
        batch_info = BatchInfo.objects.create(
            date_received=parse_date(kwargs.get('date_received')),
            pack_size=kwargs.get('pack_size'),
            quantity_received=kwargs.get('quantity_received'),
            expiry_date=parse_date(kwargs.get('expiry_date')),
            unit_cost=kwargs.get('unit_cost'),
            commentary=kwargs.get('commentary'),
            supplier=supplier_instance,
            outlet=outlet,
            user=user
        )
        for product_id in products:
            product_instance = get_model_object(Product, 'id', product_id)
            batch_info.product.add(product_instance)
        batch_info.save()
        message = [f'Batch successfully created']
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
        quantity_received = graphene.Int()
        expiry_date = graphene.String()
        unit_cost = graphene.Float()
        commentary = graphene.String()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @batch_info_instance
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        batch_id = kwargs.get('batch_id')
        products = kwargs.get('product')
        supplier_id = kwargs.get('supplier_id')
        batch_info = get_model_object(BatchInfo, 'id', batch_id)
        if products:
            batch_info.product.clear()
            for product_id in products:
                product_instance = get_model_object(Product, 'id', product_id)
                batch_info.product.add(product_instance)
        if supplier_id:
            supplier_instance = get_model_object(
                Suppliers, 'supplier_id', supplier_id)
            batch_info.supplier = supplier_instance
        for (key, value) in kwargs.items():
            if key is not None:
                if key in ('batch_id', 'supplier_id', 'product'):
                    continue
                if key in ('date_received', 'expiry_date'):
                    value = parse_date(value)
                setattr(batch_info, key, value)
        batch_info.save()
        message = [f'Batch with number {batch_info.batch_no} '
                   f'successfully updated']
        return UpdateBatchInfo(message=message, batch_info=batch_info)


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
