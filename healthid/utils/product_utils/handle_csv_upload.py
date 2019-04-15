import csv
from healthid.apps.products.models import Product
from rest_framework.exceptions import ValidationError, NotFound
from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import ProductCategory
from healthid.apps.products.models import MeasurementUnit
from django.core.exceptions import ObjectDoesNotExist


class HandleCsvValidations(object):
    def handle_csv_upload(self, io_string):
        for col in csv.reader(io_string):
            product_name = Product.objects.filter(product_name=col[1]).first()
            if len(col) != 13:
                message = {"error": "missing column(s)"}
                raise ValidationError(message)
            supplier_id = self.get_id(Suppliers, col[10], 'Supplier')
            product_category_id = self.get_id(ProductCategory, col[0],
                                              'Product category')
            backup_supplier_id = self.get_id(Suppliers, col[11],
                                             'backup_supplier')
            measurement_unit_id = self.get_id(MeasurementUnit, col[2],
                                              'measerement_unit')
            if product_name:
                message = {
                    "error":
                    "Product with product name {} alredy exists.".format(
                        product_name)
                }
                raise ValidationError(message)

            instance = Product(
                product_category_id=product_category_id,
                product_name=col[1],
                measurement_unit_id=measurement_unit_id,
                pack_size=col[3],
                description=col[4],
                brand=col[5],
                manufacturer=col[6],
                vat_status=col[7],
                quality=col[8],
                sales_price=col[9],
                prefered_supplier_id=supplier_id,
                backup_supplier_id=backup_supplier_id,
                tags=col[12])
            instance.save()

    def get_id(self, model, value, name):
        try:
            model_instance = model.objects.get(name=value)
            return model_instance.id
        except ObjectDoesNotExist:
            message = {"error": f"{name} with name {value} doesnot exist"}
            raise NotFound(message)
