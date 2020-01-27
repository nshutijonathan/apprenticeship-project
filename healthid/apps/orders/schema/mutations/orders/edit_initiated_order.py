import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import Order, AutoFillProducts
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.orders.schema.order_query import OrderType
from healthid.apps.products.models import Product
from healthid.apps.products.schema.product_query import AutofillProductType
from healthid.utils.messages.common_responses import (
    SUCCESS_RESPONSES, ERROR_RESPONSES)


class EditInitiateOrder(graphene.Mutation):
    """
    Mutation to edit an initiated order

    args:
        order_id(int): id of the initiated order to be edited
        name(str): name of the order to edit
        delivery_date(date): expected delivery date
        product_autofill(bool): toggles automatic filling in of the order's
                                products
        supplier_autofill(bool): toggles automatic filling in of the order's
                                 suppliers
        destination_outlet(int): id of the outlet destination

    returns:
        order(obj): 'Order' object detailing the edited order
        success(str): success message confirming edit of the order
    """

    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        order_id = graphene.Int(required=True)
        name = graphene.String()
        delivery_date = graphene.Date()
        product_autofill = graphene.Boolean()
        supplier_autofill = graphene.Boolean()
        destination_outlet_id = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs['order_id']
        order = get_model_object(Order, 'id', order_id)

        for(key, value) in kwargs.items():
            setattr(order, key, value)

        with SaveContextManager(order) as order:
            success = 'Order Edited Successfully!'
            return InitiateOrder(order=order, success=success)


class EditAutofillItems(graphene.Mutation):
    """
    Mutation to edit an autofill generated information table

    args:
        autofill_item_id(int): id of the item in a row
        autofill_quantity(int): quantity of the product generated
        preferred_supplier_id(int): preferred supplier generated
        backup_supplier_id(int): backup supplier generated

    returns:
        order(obj): 'Order' object detailing the edited order
        success(str): success message confirming edit of the table inforamation
    """

    message = graphene.String()
    error = graphene.String()
    updated_fields = graphene.Field(AutofillProductType)

    class Arguments:
        autofill_item_id = graphene.Int(required=True)
        autofill_quantity = graphene.Int()
        preferred_supplier_id = graphene.Int()
        backup_supplier_id = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        autofill_item_id = kwargs.get("autofill_item_id")
        autofill_quantity = kwargs.get('autofill_quantity')
        preferred_supplier_id = kwargs.get('preferred_supplier_id')
        backup_supplier_id = kwargs.get('backup_supplier_id')
        update_fields = get_model_object(
            AutoFillProducts, 'id', autofill_item_id)
        product = Product.objects.filter(
            product_name=update_fields.product_name).first()
        if autofill_quantity:
            if autofill_quantity > product.reorder_max:
                raise GraphQLError(
                    f"you can not exceed the quantity of {product.reorder_max}")
            update_fields.autofill_quantity = autofill_quantity
        if preferred_supplier_id:
            update_fields.preferred_supplier_id = preferred_supplier_id
        if backup_supplier_id:
            update_fields.backup_supplier_id = backup_supplier_id

        if autofill_quantity or preferred_supplier_id or backup_supplier_id:
            update_fields.save()
            success = 'successfully edited'
            update_fields = update_fields
            return EditAutofillItems(updated_fields=update_fields, message=success)
        return {"message": "You did not edit anything"}


class DeleteAutofillItem(graphene.Mutation):
    """
    Mutation that deletes one or more records 
    in the 'autofill order table' model.

    Arguments:
        kwargs(dict): contains the id of the 'autofill details'
                        record to be deleted.

    Returns:
        message(str): confirms successful record(s) deletion
    """

    class Arguments:
        autofill_item_id = graphene.List(graphene.Int, required=True)

    message = graphene.Field(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        autofill_item_ids = kwargs.get('autofill_item_id')
        success_message = SUCCESS_RESPONSES["deletion_success"].format(
            "item(s)"
        )
        for autofill_item_id in autofill_item_ids:
            remove_item = get_model_object(
                AutoFillProducts,
                'id',
                autofill_item_id
            )
            remove_item.hard_delete()
        return DeleteAutofillItem(message=success_message)
