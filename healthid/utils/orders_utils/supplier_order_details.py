from itertools import groupby
from healthid.apps.orders.models.orders import SupplierOrderDetails
from healthid.utils.app_utils.database import SaveContextManager


def create_suppliers_order_details(order, supplier=None):
    """
    function to generate supplier order details for an order

    Args:
        order(obj): order whose supplier order details are to be
                    generated

    Returns:
        list: suppliers order details of a particular order
    """
    order_details = order.orderdetails_set.all().order_by('supplier')
    order_details_by_suppliers = [list(result) for key, result in groupby(
        order_details, key=lambda order_detail: order_detail.supplier)]
    suppliers_order_details = []
    for order_details_per_supplier in order_details_by_suppliers:
        supplier_name = order_details_per_supplier[0].supplier
        check_duplicate = SupplierOrderDetails.objects.filter(
            order=order,
            supplier=supplier_name
        ).exists()
        supplier_order_details = SupplierOrderDetails(
            order=order,
            supplier=order_details_per_supplier[0].supplier)
        if not check_duplicate:
            with SaveContextManager(
                supplier_order_details, model=SupplierOrderDetails
            ) as supplier_order_details:
                suppliers_order_details.append(supplier_order_details)
        else:
            current_supplier_detail = SupplierOrderDetails.objects.get(
                order=order,
                supplier=supplier_name
            )
            suppliers_order_details.append(current_supplier_detail)
    return suppliers_order_details
