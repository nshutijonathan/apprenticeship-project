from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.products.models import (DispensingSize, Product,
                                           ProductCategory)


def map_quickbooks_data_helper(row, business, user, default_quickbox_supplier):
    product_name = row.get('Item Name')
    brief_description = row.get('Brief Description') or ''
    item_description = row.get('Item Description') or ''
    manufacturer = row.get('Manufacturer')
    backup_supp = row.get('Vendor Name 2')
    price = row.get('Regular Price')
    base_unit_of_measure = row.get(
        'Base Unit of Measure')
    attributes = row.get('Attributes')
    preferred_supp = row.get('Vendor Name')
    department_name = row.get('Department Name')
    dispensing_size = base_unit_of_measure or attributes
    description = (brief_description+' '+item_description) if (
        brief_description+item_description) else 'n/a'
    qty_1 = row.get('Qty 1')

    product_meta_args = {
        'Alternate Lookup': row.get('Alternate Lookup'),
        'Size': row.get('Size'),
        'Average Unit Cost': row.get('Average Unit Cost'),
        'MSRP': row.get('MSRP'),
        'Custom Price 1': row.get('Custom Price 1'),
        'Custom Price 2': row.get('Custom Price 2'),
        'Custom Price 3': row.get('Custom Price 3'),
        'Custom Price 4': row.get('Custom Price 4'),
        'UPC ': row.get('UPC'),
        'Order By Unit': row.get('Order By Unit'),
        'Sell By Unit': row.get('Sell By Unit'),
        'Item Type': row.get('Item Type'),
        'Income Account': row.get('Income Account'),
        'COGS Account': row.get('COGS Account'),
        'Asset Account': row.get('Asset Account'),
        'Print Tags': row.get('Print Tags'),
        'Unorderable': row.get('Unorderable'),
        'Serial Tracking': row.get('Serial Tracking'),
        'Department Code': row.get('Department Code'),
        'Vendor Code': row.get('Vendor Code'),
        'Qty 2': row.get('Qty 2'),
        'On Order Qty': row.get('On Order Qty'),
        'unit_cost': row.get('Order Cost')
    }
    preferred_supplier = Suppliers.objects.filter(
        supplier_id=preferred_supp).first()
    backup_supplier = Suppliers.objects.filter(
        supplier_id=backup_supp).first()
    check_product_duplicates = Product.objects.filter(
        product_name=product_name,
        business_id=business.id
    )
    if not check_product_duplicates and product_name:
        get_product_category, create_product_category =\
            ProductCategory.objects.get_or_create(
                name=department_name, business_id=business.id)
        product_category = get_product_category or create_product_category
        if dispensing_size:
            get_dispensing_size_id, create_dispensing_size_id =\
                DispensingSize.objects.get_or_create(
                    name=dispensing_size)
            dispensing_size = get_dispensing_size_id or create_dispensing_size_id
        product_instance = Product(
            product_name=product_name,
            description=description,
            brand='n/a',
            manufacturer=manufacturer,
            backup_supplier_id=backup_supplier.id if backup_supplier else None,
            dispensing_size_id=dispensing_size.id if dispensing_size else None,
            preferred_supplier_id=preferred_supplier.id if preferred_supplier else default_quickbox_supplier.id,
            product_category_id=product_category.id if product_category else None,
            loyalty_weight=2,
            sales_price=price,
            vat_status=True,
            is_approved=True,
            business_id=business.id,
            is_active=True,
            user_id=user.id if user else None
        )

        return {'product_instance': product_instance, 'product_meta_args': product_meta_args}

    return None
