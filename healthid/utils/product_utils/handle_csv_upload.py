import csv

from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import (MeasurementUnit, Product,
                                           ProductCategory)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)


class HandleCsvValidations(object):
    def handle_csv_upload(self, io_string):
        for row in csv.reader(io_string):
            if len(row) != 13:
                message = {"error": "missing column(s)"}
                raise ValidationError(message)

            product_category = get_model_object(
                ProductCategory, 'name', row[0], error_type=NotFound)
            supplier = get_model_object(
                Suppliers, 'name', row[10], error_type=NotFound)
            backup_supplier = get_model_object(
                Suppliers, 'name', row[11], error_type=NotFound)
            measurement_unit = get_model_object(
                MeasurementUnit, 'name', row[2], error_type=NotFound)

            product_instance = Product(
                product_category_id=product_category.id,
                product_name=row[1],
                measurement_unit_id=measurement_unit.id,
                pack_size=row[3],
                description=row[4],
                brand=row[5],
                manufacturer=row[6],
                vat_status=row[7],
                quality=row[8],
                sales_price=row[9],
                prefered_supplier_id=supplier.id,
                backup_supplier_id=backup_supplier.id,
                unit_cost=10.34,
                tags=row[12])
            params = {'model_name': 'Product', 'field': 'product_name',
                      'value': row[1], 'error_type': ValidationError}
            with SaveContextManager(product_instance, **params):
                pass
