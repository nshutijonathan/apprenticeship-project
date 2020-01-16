from healthid.apps.products.models import ProductMeta

product_meta_object = {
    "global_upc": "",
    "str_oh_qty": "",
    "cost": "",
    "price": ""
}


def add_product_metadata(product, items):
    for (key, value) in items.items():
        if key in product_meta_object and value:
            ProductMeta.objects.create(
                product=product, dataKey=key, dataValue=value
            )
