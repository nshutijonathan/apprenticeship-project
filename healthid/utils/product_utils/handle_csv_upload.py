import csv
from django.utils.dateparse import parse_date
from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.products.models import (BatchInfo, DispensingSize, Product,
                                           ProductCategory, Quantity)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.product_utils.product import \
    generate_reorder_points_and_max
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.utils.product_utils.validate_products_csv_upload import\
    validate_products_csv_upload


class HandleCsvValidations(object):
    def handle_csv_upload(self, io_string):
        """
        Parses products information from an appropriately formatted CSV file
        and save them.

        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of products in CSV format

        returns:
            int: the number of saved products
        """
        params = {'model': Product, 'error_type': ValidationError}
        [product_count, duplicated_products] = [0, []]

        products = validate_products_csv_upload(io_string)
        product_names = Product.objects.values_list('product_name', flat=True)

        for row in products:
            product_name = row.get('name') or row.get('product name')
            product_category = get_model_object(ProductCategory,
                                                'name__iexact',
                                                row.get('category') or row.get(
                                                    'product category'),
                                                error_type=NotFound)
            supplier = get_model_object(Suppliers,
                                        'email__iexact',
                                        row.get('preferred supplier'),
                                        error_type=NotFound,
                                        label='email')
            backup_supplier = get_model_object(Suppliers,
                                               'email__iexact',
                                               row.get('backup supplier'),
                                               error_type=NotFound,
                                               label='email')
            dispensing_size = get_model_object(DispensingSize,
                                               'name__iexact',
                                               row.get('dispensing size') or
                                               row.get('measurement unit'),
                                               error_type=NotFound,
                                               label='Dispensing size')
            vat_status = row.get('vat status').lower() == 'vat' or False\
                if row.get('vat status')\
                else product_category.is_vat_applicable

            loyalty_weight = row.get('loyalty weight')\
                if str(row.get('loyalty weight')).isdigit()\
                else product_category.loyalty_weight
            image = row.get('image') or row.get('product image')
            if product_name \
                    not in product_names and product_category.outlet_id:
                product_instance = Product(
                    product_category_id=product_category.id,
                    outlet_id=product_category.outlet_id,
                    product_name=product_name,
                    dispensing_size_id=dispensing_size.id,
                    description=row.get('description') or '',
                    brand=row.get('brand') or '',
                    manufacturer=row.get('manufacturer') or '',
                    vat_status=vat_status,
                    preferred_supplier_id=supplier.id,
                    backup_supplier_id=backup_supplier.id,
                    tags=row.get('tags') or '',
                    image=image or '',
                    loyalty_weight=loyalty_weight)

                with SaveContextManager(product_instance, **params):
                    product_count += 1
            else:
                duplicated_products.append(
                    ERROR_RESPONSES['duplication_error'].
                    format(row.get('name') or row.get('product name')))
        return {
            'product_count': product_count,
            'duplicated_products': duplicated_products
        }

    def handle_batch_csv_upload(self, user, batch_info_csv):
        """
        Parses batch information from an appropriately formatted CSV file.
        Creates and saves new 'BatchInfo' instances.
        Updates the product quantities based on the new batches.

        arguments:
            user(obj): contains a 'User' instance
            batch_info_csv(obj): 'io.StringIO' object representing
                                 the batch info CSV

        returns:
            None
        """

        batch_record_format = [
            'Product',
            'Supplier',
            'Date Received',
            'Expiry Date',
            'Unit Cost',
            'Quantity Received',
            'Service Quality',
            'Delivery Promptness'
        ]
        true_strings = ['TRUE', 'True', 'true', 't']
        false_strings = ['FALSE', 'False', 'false', 'f']

        # produces the column header row of the CSV
        # from the iterator returned by csv.reader()
        column_header = next(csv.reader(batch_info_csv))

        if column_header == batch_record_format:
            for batch_record in csv.reader(batch_info_csv):
                product_id = get_model_object(
                    Product,
                    'product_name',
                    batch_record[0],
                    error_type=NotFound
                ).id
                supplier_id = get_model_object(
                    Suppliers,
                    'name',
                    batch_record[1],
                    error_type=NotFound
                ).id

                # check if batch expiry date occurs before delivery date.
                # 'batch_record[3]' and 'batch_record[2]' represent the
                # 'Expiry Date' and 'Delivery Date' CSV records respectively.
                if batch_record[3] < batch_record[2]:
                    raise ValidationError(
                        PRODUCTS_ERROR_RESPONSES["batch_expiry_error"].format
                        (batch_record[0])
                    )

                # converts a 'True' or 'False' string from the
                # 'Delivery Promptness' CSV column into a Python boolean.
                # 'batch_record[7]' represents the 'Delivery Promptness'
                #  CSV record.
                if batch_record[7] in true_strings:
                    batch_record[7] = True
                elif batch_record[7] in false_strings:
                    batch_record[7] = False
                else:
                    raise ValidationError(
                        PRODUCTS_ERROR_RESPONSES["batch_bool_error"]
                    )

                batch_info_args = {
                    'product_id': product_id,
                    'supplier_id': supplier_id,
                    'date_received': batch_record[2],
                    'expiry_date': batch_record[3],
                    'unit_cost': float(batch_record[4]),
                    'quantity': int(batch_record[5]),
                    'service_quality': int(batch_record[6]),
                    'delivery_promptness': batch_record[7]
                }
                self.create_batch_info(user, **batch_info_args)
        else:
            raise ValidationError(PRODUCTS_ERROR_RESPONSES["batch_csv_error"])

    @batch_info_instance
    def create_batch_info(self, user, **kwargs):
        quantity = kwargs.pop('quantity')
        kwargs['date_received'] = parse_date(kwargs.get('date_received'))
        kwargs['expiry_date'] = parse_date(kwargs.get('expiry_date'))

        batch_info = BatchInfo(user=user)
        for key, value in kwargs.items():
            setattr(batch_info, key, value)

        with SaveContextManager(batch_info, model=BatchInfo) as batch_info:
            quantity = Quantity(
                batch=batch_info, quantity_received=quantity,
                quantity_remaining=quantity, is_approved=True)
            quantity.save()
            generate_reorder_points_and_max(batch_info.product)
