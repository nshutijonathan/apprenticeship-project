from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import MeasurementUnit, ProductCategory
from healthid.utils.app_utils.database import get_model_object


def handle_validation(**kwargs):

    if kwargs.get('product_category_id'):
        get_model_object(ProductCategory, 'id',
                         kwargs.get('product_category_id'))

    if kwargs.get('measurement_unit_id'):
        get_model_object(MeasurementUnit, 'id',
                         kwargs.get('measurement_unit_id'))

    if kwargs.get('prefered_supplier_id'):
        get_model_object(Suppliers, 'id', kwargs.get('prefered_supplier_id'))

    if kwargs.get('backup_supplier_id'):
        get_model_object(Suppliers, 'id', kwargs.get('backup_supplier_id'))
