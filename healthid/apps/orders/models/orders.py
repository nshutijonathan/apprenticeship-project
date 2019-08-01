from datetime import timedelta
from django.db import models
from django.conf import settings

from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.app_utils.database import get_model_object


class Order(BaseModel):
    '''Class to handle order data
    '''
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(
        max_length=9, default=id_gen, editable=False
    )
    name = models.TextField(null=False)
    product_autofill = models.BooleanField(default=True)
    supplier_autofill = models.BooleanField(default=True)
    destination_outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        default=1
    )
    delivery_date = models.DateField()
    sent_status = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)


class OrderDetails(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE,
                                 null=True)
    price = models.DecimalField(blank=True, null=True,
                                max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    @classmethod
    def check_if_duplicate(self, order_id, order_detail_object, supplier=None):
        """
        Adds a supplier value to the 'OrderDetail' object
        Checks for duplicate order details records in the database
        If not duplicated, bulk creates new 'OrderDetail' records

        Arguments:
            order_id(int): Id of the 'Order' that the
                          'OrderDetail' object is for
            order_detail_object(list): list of 'OrderDetail' model objects
                                       to be saved
            supplier(iter): iterable of suppliers whose order details are
                      being created

        Returns:
            created_order(obj): latest order detail created
        """
        detail_object_list = []
        for detail_object in order_detail_object:
            if supplier is None:
                product = get_model_object(
                    Product,
                    'id',
                    detail_object.product_id
                )
                supplier_id = product.preferred_supplier.id
            else:
                supplier_id = next(supplier)
            check_duplicate = self.objects.filter(
                order__id=order_id,
                product__id=detail_object.product_id,
                supplier__id=supplier_id
            ).exists()

            if not check_duplicate:
                detail_object.supplier_id = supplier_id
                detail_object_list.append(detail_object)
                created_order = detail_object
            else:
                current_order_detail = OrderDetails.objects.get(
                    order__id=order_id,
                    product__id=detail_object.product_id,
                    supplier__id=supplier_id
                )
                current_order_detail.quantity = detail_object.quantity
                current_order_detail.save()
                created_order = current_order_detail

        OrderDetails.objects.bulk_create(detail_object_list)
        return created_order


class SupplierOrderDetails(BaseModel):
    """
    defines supplier order details model

    Args:
        grand_total: possible price of the order for supplier
        additional_notes: notes about the order from a supplier
        order: order the order details of a supplier belong to
        supplier: supplier of order details
    """
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"

    ORDER_STATUSES = (
        (PENDING, "Pending Approval"),
        (OPEN, "Open"),
        (CLOSED, "Closed"),
    )

    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    grand_total = models.DecimalField(blank=True, null=True,
                                      max_digits=10, decimal_places=2)
    additional_notes = models.CharField(max_length=500, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                    related_name="approved_supplier_orders",
                                    on_delete=models.CASCADE)
    marked_as_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=ORDER_STATUSES,
                              default=PENDING)

    @property
    def get_order_details(self):
        """
        get order details of a supplier based on order

        Returns:
            list: order details of a single supplier from an order
        """
        return self.order.orderdetails_set.all().filter(supplier=self.supplier)

    @property
    def get_supplier_order_name(self):
        """
        generates order name for a supplier

        Returns:
            string: combination of order name and supplier order details
                    id
        """
        return self.order.name + self.supplier_id

    @property
    def get_supplier_order_number(self):
        """
        generates order number for a supplier

        Returns:
            string: combination of order number and supplier order
                    details id
        """
        return self.order.order_number + self.supplier_id

    @property
    def deliver_to_outlets(self):
        """
        gets the outlets a supplier will deliver to

        Returns:
            list: outlets a supplier will deliver to
        """
        return self.order.destination_outlet

    @property
    def delivery_due_date(self):
        """
        gets the date the order should be delivered by

        Returns:
            date: when the supplier has to deliver the order
        """
        return self.order.delivery_date

    @property
    def payment_due_date(self):
        """
        determines when the supplier should be paid

        Returns:
            date: when the supplier expects to be paid for thr order
        """
        return self.delivery_due_date + \
            timedelta(days=self.supplier.credit_days)

    @property
    def order_status(self):
        """Returns the status of the supplier order form.

        Returns:
            status: displayable version of the status.
        """
        return self.get_status_display()
