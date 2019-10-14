import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.services import (SupplierOrderDetailsFetcher,
                                           SupplierOrderEmailSender)


class SendSupplierOrderEmails(graphene.Mutation):
    """Send Supplier Order Emails to suppliers

    Send a PDF supplier order form to the supplier listing
    all ordered items.

    Args:
        supplier_order_ids: A list of supplier order ids

    Returns:
        message: a return message
    """
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_ids = graphene.List(graphene.String,
                                           required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        supplier_order_ids = kwargs.get('supplier_order_ids')

        details_fetcher = SupplierOrderDetailsFetcher(order_id,
                                                      supplier_order_ids)
        email_sender = SupplierOrderEmailSender(details_fetcher.fetch())
        message = email_sender.send()
        return SendSupplierOrderEmails(message=message)
