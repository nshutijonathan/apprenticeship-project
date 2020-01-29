from healthid.apps.products.models import ProductMeta

product_meta_object = {
    "global_upc": "",
    "str_oh_qty": "",
    "cost": "",
    "price": "",
    'Alternate Lookup': '',
    'Size': '',
    'Average Unit Cost': '',
    'MSRP': '',
    'Custom Price 1': '',
    'Custom Price 2': '',
    'Custom Price 3': '',
    'Custom Price 4': '',
    'UPC ': '',
    'Order By Unit': '',
    'Sell By Unit': '',
    'Item Type': '',
    'Income Account': '',
    'COGS Account': '',
    'Asset Account': '',
    'Print Tags': '',
    'Unorderable': '',
    'Serial Tracking': '',
    'Department Code': '',
    'Vendor Code': '',
    'Qty 2': '',
    'On Order Qty': '',
    'unit_cost': '',
}


def add_product_metadata(product, items):
    for (key, value) in items.items():
        if key in product_meta_object and value:
            ProductMeta.objects.create(
                product=product, dataKey=key, dataValue=value
            )
