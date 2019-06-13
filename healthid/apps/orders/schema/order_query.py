import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.orders.models.orders import (
    SupplierOrderDetails, Order, OrderDetails)
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.outlets.schema.outlet_schema import OutletType
from healthid.apps.orders.models.suppliers import Suppliers


class OrderDetailsType(DjangoObjectType):
    class Meta:
        model = OrderDetails


class SupplierOrderDetailsType(DjangoObjectType):
    order_details = graphene.List(OrderDetailsType)
    supplier_order_name = graphene.String()
    supplier_order_number = graphene.String()
    deliver_to = graphene.Field(OutletType)
    delivery_due = graphene.Date()
    payment_due = graphene.Date()

    class Meta:
        model = SupplierOrderDetails

    def resolve_order_details(self, info, **kwargs):
        """
        get order details

        Returns:
            list: order details of a particular supplier and order
        """
        return self.get_order_details

    def resolve_supplier_order_name(self, info, **kwargs):
        """
        gets supplier order name

        Returns:
            string: supplier order name from supplier order details
        """
        return self.get_supplier_order_name

    def resolve_supplier_order_number(self, info, **kwargs):
        """
        gets supplier order number

        Returns:
            string: supplier order number from supplier order details
        """
        return self.get_supplier_order_number

    def resolve_deliver_to(self, info, **kwargs):
        """
        gets outlets a supplier is supposed to deliver the order to

        Returns:
            list: outlets supplier is supposed to deliver to from
                  supplier order details
        """
        return self.deliver_to_outlets

    def resolve_delivery_due(self, info, **kwargs):
        """
        gets the date a supplier is supposed to deliver the order

        Returns:
            date: date when the supplier has to deliver order from
                  supplier order details
        """
        return self.delivery_due_date

    def resolve_payment_due(self, info, **kwargs):
        """
        gets when the payment of the supplier should be paid

        Returns:
            date: when the supplier will be paid from the supplier
                  order details
        """
        return self.payment_due_date


class Query(graphene.AbstractType):
    suppliers_order_details = graphene.List(
        SupplierOrderDetailsType, order_id=graphene.Int(required=True))
    supplier_order_details = graphene.Field(
        SupplierOrderDetailsType, order_id=graphene.Int(required=True),
        supplier_id=graphene.String(required=True)
    )

    @login_required
    def resolve_suppliers_order_details(self, info, **kwargs):
        """
        gets order details for suppliers of that order

        Returns:
            list: supplier order details of a particular order
        """
        order = get_model_object(Order, 'id', kwargs.get('order_id'))
        return SupplierOrderDetails.objects.filter(order=order)

    @login_required
    def resolve_supplier_order_details(self, info, **kwargs):
        order = get_model_object(Order, 'id', kwargs.get('order_id'))
        supplier = get_model_object(Suppliers, 'id', kwargs.get('supplier_id'))
        return SupplierOrderDetails.objects.filter(order=order,
                                                   supplier=supplier).first()
