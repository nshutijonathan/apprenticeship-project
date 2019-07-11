import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.apps.sales.models import (SalesPrompt, Sale)
from healthid.apps.sales.schema.sales_schema import (
    SalesPromptType, SaleType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.receipts.models import Receipt
from healthid.apps.receipts.schema.receipt_schema import ReceiptType
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class CreateSalesPrompts(graphene.Mutation):
    """
    This Creates a Sales Prompt for a group of products particular Product
    """
    sales_prompts = graphene.List(SalesPromptType)
    message = graphene.String()

    class Arguments:
        prompt_titles = graphene.List(graphene.String, required=True)
        descriptions = graphene.List(graphene.String, required=True)
        product_ids = graphene.List(graphene.Int, required=True)
        outlet_ids = graphene.List(graphene.Int, required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        titles = kwargs.get('prompt_titles')
        prompt_descriptions = kwargs.get('descriptions')
        outlet_ids = kwargs.get('outlet_ids')
        sales_prompt_count = 0
        valid_list = all(len(product_ids) == len(list_inputs)
                         for list_inputs in
                         [titles, prompt_descriptions, outlet_ids])

        if not valid_list or len(product_ids) < 1:

            raise GraphQLError(SALES_ERROR_RESPONSES["incomplete_list"])

        for title, description in zip(titles, prompt_descriptions):
            if title.strip() == "" or description.strip() == "":
                raise GraphQLError(SALES_ERROR_RESPONSES["title_error"])
        created_prompts = []
        for index, title in enumerate(titles, 0):

            params = {'model': SalesPrompt}
            sales_prompt = SalesPrompt(
                prompt_title=title.title(),
                description=prompt_descriptions[index],
                product_id=get_model_object(Product, 'id',
                                            product_ids[index]).id,
                outlet_id=get_model_object(Outlet, 'id',
                                           outlet_ids[index]).id)

            with SaveContextManager(sales_prompt, **params) as sales_prompt:
                created_prompts.append(sales_prompt)
                sales_prompt_count += 1

        return CreateSalesPrompts(
            sales_prompts=created_prompts,
            message=SUCCESS_RESPONSES[
                    "creation_success"].format(
                                        "Sales prompt " + str(
                                                         sales_prompt_count)))


class UpdateSalesPrompt(graphene.Mutation):
    """
    This Updates a Sales prompt
    """
    success = graphene.String()
    salesPrompt = graphene.Field(SalesPromptType)

    class Arguments:
        id = graphene.Int(required=True)
        prompt_title = graphene.String()
        description = graphene.String()
        product_id = graphene.Int()
        outlet_id = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, id, **kwargs):
        salesPrompt = get_model_object(SalesPrompt, 'id', id)
        for key, value in kwargs.items():
            if key in ["prompt_title", "description"]:
                if value.strip() == "":
                    raise GraphQLError(SALES_ERROR_RESPONSES["title_error"])
            setattr(salesPrompt, key, value)
        params = {'model': SalesPrompt}
        with SaveContextManager(salesPrompt, **params) as salesPrompt:
            return UpdateSalesPrompt(
                success=SUCCESS_RESPONSES[
                        "update_success"].format("Sales prompt"),
                salesPrompt=salesPrompt)


class DeleteSalesPrompt(graphene.Mutation):
    """
    This deletes a Sales prompt
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, id):
        user = info.context.user
        prompt = get_model_object(SalesPrompt, 'id', id)
        prompt.delete(user)
        return DeleteSalesPrompt(
            success=SUCCESS_RESPONSES[
                    "deletion_success"].format("Sales prompt"))


class Products(graphene.InputObjectType):
    """
    This class defines necessary fields of a product to be sold
    """
    product_id = graphene.Int()
    quantity = graphene.Int()
    discount = graphene.Float()
    price = graphene.Float()
    note = graphene.String()


class CreateSale(graphene.Mutation):
    """
    Create a sale
    """
    sale = graphene.Field(SaleType)
    message = graphene.String()
    error = graphene.String()
    receipt = graphene.Field(ReceiptType)

    class Arguments:
        customer_id = graphene.String()
        outlet_id = graphene.Int(required=True)
        products = graphene.List(Products, required=True)
        discount_total = graphene.Float(graphene.Float, required=True)
        sub_total = graphene.Float(graphene.Float, required=True)
        amount_to_pay = graphene.Float(graphene.Float, required=True)
        paid_amount = graphene.Float(graphene.Float, required=True)
        change_due = graphene.Float(graphene.Float, required=True)
        payment_method = graphene.String(graphene.String, required=True)
        notes = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        new_sale = Sale()
        new_receipt = Receipt()
        sale = new_sale.create_sale(info=info, **kwargs)
        receipt = new_receipt.create_receipt(sale, kwargs.get('outlet_id'))
        return CreateSale(sale=sale,
                          receipt=receipt,
                          message='Sale was created successfully')


class Mutation(graphene.ObjectType):
    create_salesprompts = CreateSalesPrompts.Field()
    delete_salesprompt = DeleteSalesPrompt.Field()
    update_salesprompt = UpdateSalesPrompt.Field()
    create_sale = CreateSale.Field()
