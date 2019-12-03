import graphene

from healthid.apps.orders.schema.mutations.orders.initiate_order \
    import InitiateOrder
from healthid.apps.orders.schema.mutations.orders.edit_initiated_order \
    import EditInitiateOrder
from healthid.apps.orders.schema.mutations.orders.add_order_details \
    import AddOrderDetails
from healthid.apps.orders.schema.mutations.orders.approve_supplier_order \
    import ApproveSupplierOrder
from healthid.apps.orders.schema.mutations.orders.\
    mark_supplier_order_status_approved \
    import ChangeSupplierOrderStatus
from healthid.apps.orders.schema.mutations.orders.send_supplier_order_emails \
    import SendSupplierOrderEmails
from healthid.apps.orders.schema.mutations.orders.mark_supplier_order_as_sent \
    import MarkSupplierOrderAsSent
from healthid.apps.orders.schema.mutations.orders.delete_order_detail \
    import DeleteOrderDetail
from healthid.apps.orders.schema.mutations.orders.close_order \
    import CloseOrder


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
    edit_initiated_order = EditInitiateOrder.Field()
    add_order_details = AddOrderDetails.Field()
    approve_supplier_order = ApproveSupplierOrder.Field()
    mark_supplier_order_status_approved = ChangeSupplierOrderStatus.Field()
    send_supplier_order_emails = SendSupplierOrderEmails.Field()
    mark_supplier_order_as_sent = MarkSupplierOrderAsSent.Field()
    delete_order_detail = DeleteOrderDetail.Field()
    close_order = CloseOrder.Field()
