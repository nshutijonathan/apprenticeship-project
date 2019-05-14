from datetime import datetime

import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import StockCountTemplate
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.stock_utils.stock_counts import stock_counts


class StockCountTemplateType(DjangoObjectType):
    class Meta:
        model = StockCountTemplate


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
        params = {'moel_name': StockCountTemplate}
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
        send_mail.send()
        message = 'Stock template was successfully deleted'
        return DeleteStockCountTemplate(success=message)


class Mutation(graphene.ObjectType):
    create_stock_count_template = CreateStockCountTemplate.Field()
    edit_stock_count_template = EditStockCountTemplate.Field()
    delete_stock_count_template = DeleteStockCountTemplate.Field()
