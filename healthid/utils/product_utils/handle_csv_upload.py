import csv

from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.products.models import (MeasurementUnit, Product,
                                           ProductCategory)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)


class HandleCsvValidations(object):
    def handle_csv_upload(self, io_string):
        params = {'model': Product, 'error_type': ValidationError}
        product_count = 0

        for row in csv.reader(io_string):
            if len(row) != 10:
                message = {"error": "csv file missing column(s)"}
                raise ValidationError(message)

            product_category = get_model_object(
                ProductCategory, 'name', row[0], error_type=NotFound)
            supplier = get_model_object(
                Suppliers, 'name', row[7], error_type=NotFound)
            backup_supplier = get_model_object(
                Suppliers, 'name', row[8], error_type=NotFound)
            measurement_unit = get_model_object(
                MeasurementUnit, 'name', row[2], error_type=NotFound)

            product_instance = Product(
                product_category_id=product_category.id,
                product_name=row[1],
                measurement_unit_id=measurement_unit.id,
                description=row[3],
                brand=row[4],
                manufacturer=row[5],
                vat_status=True if row[6].lower() == 'vat' else False,
                preferred_supplier_id=supplier.id,
                backup_supplier_id=backup_supplier.id,
                unit_cost=10.34,
                tags=row[9])
            with SaveContextManager(product_instance, **params):
                pass

            product_count += 1

        return product_count
