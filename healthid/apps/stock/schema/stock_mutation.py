from datetime import datetime

import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.apps.stock.models import (StockCount, StockCountRecord,
                                        StockCountTemplate)
from healthid.apps.stock.schema.stock_query import (StockCountTemplateType,
                                                    StockCountType)
from healthid.apps.stock.schema.stock_transfer_mutations import (
    CloseStockTransfer, OpenStockTransfer)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.error_handler import errors
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.app_utils.validators import check_validity_of_ids
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.notifications_utils.handle_notifications import notify
from healthid.utils.stock_utils.stock_count_utils import validate_stock
from healthid.utils.stock_utils.stock_counts import stock_counts


class CreateStockCountTemplate(graphene.Mutation):
    stock_template = graphene.Field(StockCountTemplateType)
    success = graphene.String()

    class Arguments:
        product_ids = graphene.List(graphene.Int, required=True)
        event_id = graphene.Int(required=True)
        assigned_user_ids = graphene.List(graphene.String, required=True)
        designated_user_ids = graphene.List(graphene.String, required=True)
        outlet_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        template_instance = StockCountTemplate()
        template_fields = stock_counts.get_template_fields(**kwargs)
        with SaveContextManager(template_instance) as stock_tempalate:
            stock_tempalate = stock_counts.add_fields_to_template(
                template_instance,
                **template_fields
            )
            stock_tempalate.save()
        to_email = stock_tempalate.assigned_users.values_list(
            'email', flat=True)
        email_stock_template = 'email_alerts/stocks/stock_email.html'
        subject = 'Stock counts alert'
        context = {
            'schedule_time': datetime.strftime(
                stock_tempalate.schedule_time.start_date, "%d-%b-%Y"),
            'by': str(info.context.user.email),
            'template_type': 'Stock counts',
            'small_text_detail': 'Hello, you have been assigned to carry'
                                 ' out stock counts'
        }
        send_mail = SendMail(email_stock_template, context, subject, to_email)
        send_mail.send()
        message = 'successfuly created stock count template'
        return CreateStockCountTemplate(
            stock_template=stock_tempalate, success=message)


class EditStockCountTemplate(graphene.Mutation):
    stock_template = graphene.Field(StockCountTemplateType)
    success = graphene.String()

    class Arguments:
        template_id = graphene.Int(required=True)
        product_ids = graphene.List(graphene.Int)
        event_id = graphene.Int()
        assigned_user_ids = graphene.List(graphene.String)
        designated_user_ids = graphene.List(graphene.String)
        outlet_id = graphene.Int()

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        template_instance = get_model_object(
            StockCountTemplate, 'id', kwargs.get('template_id'))
        template_fields = stock_counts.get_template_fields(**kwargs)
        stock_tempalate = stock_counts.add_fields_to_template(
            template_instance,
            **template_fields
        )
        to_email = stock_tempalate.assigned_users.values_list(
            'email', flat=True)
        email_stock_template = 'email_alerts/stocks/stock_email.html'
        subject = 'Stock counts template updated'
        context = {
            'schedule_time': datetime.strftime(
                stock_tempalate.schedule_time.start_date, "%d-%b-%Y"),
            'by': str(info.context.user.email),
            'template_type': 'Stock counts',
            'small_text_detail': 'Hello, stock counts shcedule has '
                                 'been modified'
        }
        params = {'model': StockCountTemplate}
        with SaveContextManager(stock_tempalate, **params) as stock_tempalate:
            send_mail = SendMail(email_stock_template,
                                 context, subject, to_email)
            send_mail.send()
            message = 'successfuly edited stock count template'
            return EditStockCountTemplate(
                stock_template=stock_tempalate, success=message)


class DeleteStockCountTemplate(graphene.Mutation):
    stock_template = graphene.Field(StockCountTemplateType)
    success = graphene.String()
    errors = graphene.String()

    class Arguments:
        template_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        user = info.context.user
        stock_tempalate = get_model_object(
            StockCountTemplate, 'id', kwargs.get('template_id'))
        to_email = stock_tempalate.assigned_users.values_list(
            'email', flat=True)
        email_stock_template = 'email_alerts/stocks/stock_email.html'
        subject = 'Stock counts template canceled'
        context = {
            'schedule_time': datetime.strftime(
                stock_tempalate.schedule_time.start_date, "%d-%b-%Y"),
            'by': str(info.context.user.email),
            'template_type': 'Stock counts',
            'small_text_detail': 'Hello, stock counts has been canceled'
        }
        send_mail = SendMail(email_stock_template, context, subject, to_email)
        stock_tempalate.delete(user)
        send_mail.send()
        message = 'Stock template was successfully deleted'
        return DeleteStockCountTemplate(success=message)


class VarianceEnum(graphene.Enum):
    IncorrectInitialEntry = 'Incorrect Initial Entry'
    ReturnedToDistributor = 'Returned to Distributor'
    DamagedProduct = 'Damaged Product'
    WrongSale = 'Wrong Sale'
    UnIdentified = 'Unidentified'
    NoVariance = 'No Variance'
    Others = 'Others'


class InitiateStockCount(graphene.Mutation):
    """
        Mutation to create a Stock Count Information
    """
    stock_count = graphene.Field(StockCountType)

    class Arguments:
        batch_info = graphene.List(graphene.String, required=True)
        stock_template_id = graphene.Int(required=True)
        product = graphene.Int(required=True)
        quantity_counted = graphene.List(graphene.Int, required=True)
        variance_reason = graphene.Argument(VarianceEnum, required=True)
        remarks = graphene.String()
        specify_reason = graphene.String()
        is_completed = graphene.Boolean(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        validate_stock.stock_validate(kwargs)
        batch_info = kwargs.get('batch_info')
        quantity_counted = kwargs.get('quantity_counted')
        product = kwargs.get('product')
        product_instance = get_model_object(Product, 'id', product)
        all_batches = product_instance.batch_info.all()
        stock_template = get_model_object(
            StockCountTemplate, 'id', kwargs.get('stock_template_id'))
        stock_template_products = stock_template.products.all()
        if product_instance not in stock_template_products:
            errors.custom_message(
                'Product must belong to this stock template')
        for batch in batch_info:
            batch_instance = get_model_object(BatchInfo, 'id', batch)
            if batch_instance not in all_batches:
                errors.custom_message(
                    f'Product {product_instance.product_name} '
                    f'does not have a batch with id {batch_instance}')
        stock_count = StockCount()
        validate_stock.add_stock(kwargs, stock_count)
        with SaveContextManager(stock_count) as stock_count:
            message = [f' Stock Count has been saved in progress']
            for index, value in enumerate(batch_info):
                record_instance = StockCountRecord.objects.create(
                    quantity_counted=quantity_counted[index],
                    batch_info_id=value,
                )
                stock_count.stock_count_record.add(record_instance)
            if stock_count.is_completed:
                users_instance = \
                    stock_count.stock_template.designated_users.all()
                email_stock_count = \
                    'email_alerts/stocks/stock_count_email.html'
                event_name = 'stock_count_approval'
                subject = 'Stock Count sent for approval'
                context = {
                    'template_type': 'Stock Count Approval',
                    'small_text_detail': 'Stock Count Details',
                    'email': str(info.context.user.email),
                    'quantity_counted': str(stock_count.quantity_counted),
                    'variance_reason': str(stock_count.variance_reason),
                    'product_quantity': str(stock_count.product.quantity)
                }
                notify(
                    users=users_instance,
                    message=subject, event_name=event_name,
                    subject=context, html_body=email_stock_count,
                )
                message = [f'Stock Count has been sent for approval']
        return InitiateStockCount(message=message, stock_count=stock_count)


class UpdateStockCount(graphene.Mutation):
    stock_count = graphene.Field(StockCountType)

    class Arguments:
        batch_info = graphene.List(graphene.String)
        stock_count_id = graphene.String(required=True)
        stock_template_id = graphene.Int()
        product = graphene.Int()
        quantity_counted = graphene.List(graphene.Int)
        variance_reason = graphene.Argument(VarianceEnum)
        remarks = graphene.String()
        specify_reason = graphene.String()
        is_completed = graphene.Boolean()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        batch_info = kwargs.get('batch_info')
        quantity_counted = kwargs.get('quantity_counted')
        stock_count_id = kwargs.get('stock_count_id')
        validate_stock.stock_validate(kwargs)
        validate_stock.check_empty_id(stock_count_id, name='Stock Count')
        stock_count = get_model_object(StockCount, 'id', stock_count_id)
        validate_stock.check_approved_stock(info, stock_count)
        validate_stock.add_stock(kwargs, stock_count)
        validate_stock.validate_batch_ids(stock_count, batch_info)
        with SaveContextManager(stock_count) as stock_count:
            if batch_info and quantity_counted:
                for field, data in enumerate(batch_info):
                    record_instance = \
                        stock_count.stock_count_record.get(batch_info=data)
                    record_instance.quantity_counted = \
                        quantity_counted[field]
                    record_instance.save()
            if stock_count.is_completed:
                users_instance = \
                    stock_count.stock_template.designated_users.all()
                email_stock_count = \
                    'email_alerts/stocks/stock_count_email.html'
                event_name = 'stock_count_approval'
                subject = 'Stock Count sent for approval'
                context = {
                    'template_type': 'Stock Count Approval',
                    'small_text_detail': 'Stock Count Details',
                    'email': str(info.context.user.email),
                    'quantity_counted': str(stock_count.quantity_counted),
                    'variance_reason': str(stock_count.variance_reason),
                    'product_quantity': str(stock_count.product.quantity)
                }
                notify(
                    users=users_instance,
                    message=subject, event_name=event_name,
                    subject=context, html_body=email_stock_count,
                )
        message = ['Stock Count has been updated successfully']
        return UpdateStockCount(
            message=message, stock_count=stock_count)


class RemoveBatchStock(graphene.Mutation):
    stock_count = graphene.Field(StockCountType)

    class Arguments:
        batch_info = graphene.List(graphene.String, required=True)
        stock_count_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        batch_info = kwargs.get('batch_info')
        validate_stock.stock_validate(kwargs)
        stock_count_id = kwargs.get('stock_count_id')
        validate_stock.check_empty_id(stock_count_id, name='Stock Count')
        stock_count = get_model_object(
            StockCount, 'id', stock_count_id)
        validate_stock.validate_batch_ids(
            stock_count, batch_info_ids=batch_info)
        if len(stock_count.stock_count_record.values_list('batch_info')) <= 1:
            errors.custom_message(
                'Stock must contain at least (one) 1 batch')
        for batch_id in batch_info:
            record_instance = stock_count.stock_count_record.get(
                batch_info=batch_id)
            stock_count.stock_count_record.remove(record_instance)
        message = [f'{len(batch_info)} Batch Deleted from stock count']
        return RemoveBatchStock(message=message, stock_count=stock_count)


class DeleteStockCount(graphene.Mutation):
    """
        Delete a Product batch Info Mutation
    """

    stock_count = graphene.Field(StockCountType)

    class Arguments:
        stock_count_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        user = info.context.user
        stock_count_id = kwargs.get('stock_count_id')
        validate_stock.check_empty_id(stock_count_id, name='Stock Count')
        stock_count = get_model_object(StockCount, 'id', stock_count_id)
        validate_stock.check_approved_stock(info, stock_count)
        message = f'Stock Count with id {stock_count.id} has been deleted'
        stock_count.delete(user)
        return DeleteStockCount(message=message)


class ReconcileStock(graphene.Mutation):
    """
      Mutation for reconciling stock count.
    """
    stock_counts = graphene.List(StockCountType)
    stock_count = graphene.Field(StockCountType)
    message = graphene.String()

    class Arguments:
        stock_count_id = graphene.String(required=True)
        batch_info = graphene.List(graphene.String, required=True)
    errors = graphene.List(graphene.String)
    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        batch_info_ids = kwargs.get('batch_info')
        stock_count_id = kwargs.get('stock_count_id')
        if stock_count_id.strip() == "":
            raise GraphQLError("Stock Count id field can't be empty")
        stock_count = get_model_object(StockCount, 'id', stock_count_id)
        stock_count_batch_ids = stock_count.stock_count_record.values_list(
            'batch_info_id', flat=True)
        message = "Batch with ids '{}' do not exist in this stock count."
        check_validity_of_ids(batch_info_ids, stock_count_batch_ids, message)
        if stock_count.is_approved:
            raise GraphQLError("Stockcount is already aproved.")
        for batch_id in batch_info_ids:
            stock_record = stock_count.stock_count_record.get(
                batch_info_id=batch_id)
            stock_record_quantity = stock_record.quantity_counted
            quantity = Quantity.objects.get(
                batch_id=batch_id, product__id=stock_count.product_id)
            quantity.quantity_received = stock_record_quantity
            quantity.save()
        stock_count.is_approved = True
        stock_count.save()
        message = 'Stock Count has been approved'
        return ReconcileStock(message=message, stock_count=stock_count)


class Mutation(graphene.ObjectType):
    initiate_stock = InitiateStockCount.Field()
    update_stock = UpdateStockCount.Field()
    delete_stock = DeleteStockCount.Field()
    remove_batch_stock = RemoveBatchStock.Field()
    create_stock_count_template = CreateStockCountTemplate.Field()
    edit_stock_count_template = EditStockCountTemplate.Field()
    delete_stock_count_template = DeleteStockCountTemplate.Field()
    reconcile_stock = ReconcileStock.Field()
    open_stock_transfer = OpenStockTransfer.Field()
    close_stock_transfer = CloseStockTransfer.Field()
