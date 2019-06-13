from itertools import groupby
from healthid.apps.orders.models.orders import SupplierOrderDetails
from healthid.utils.app_utils.database import SaveContextManager


def create_suppliers_order_details(order):
    """
    function to generate supplier order details for an order

    Args:
        order(obj): order whose supplier order details are to be
                    generated

    Returns:
        list: suppliers order details of a particular order
    """
    order_details = order.orderdetails_set.all()
    order_details_by_suppliers = [list(result) for key, result in groupby(
        order_details, key=lambda order_detail: order_detail.supplier)]
    suppliers_order_details = []
    for order_details_per_supplier in order_details_by_suppliers:
        supplier_order_details = SupplierOrderDetails(
            order=order,
            supplier=order_details_per_supplier[0].supplier)
        with SaveContextManager(
            supplier_order_details, model=SupplierOrderDetails
        ) as supplier_order_details:
            suppliers_order_details.append(supplier_order_details)
    return suppliers_order_details
