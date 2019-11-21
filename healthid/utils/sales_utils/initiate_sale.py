import math
from healthid.apps.products.models import Quantity


def initiate_sale(sold_product_instances, sold_products, sale, sale_detail,
                  batch_history):
    """
    This function create a sale detail by looping through all sold
    products and create a record in SaleDetail by adding sale Id.

    It deduct sold quantity from batch quantity
    args:
        sold_product_instances : Holds a list of product from database
        sold_products : Holds a list of sold product
        sale: Holds a sale instance
        sale_detail: Holds sale detail model passed as argument
    """
    products = zip(sold_product_instances, sold_products)
    sale_details = []
    sold_products_loyalty_points = []

    for sold_product, product_detail in products:
        product_category = sold_product.product.product_category
        loyalty_points = (product_detail.price / product_category.amount_paid) * sold_product.product.loyalty_weight  # noqa
        sold_products_loyalty_points.append(math.floor(loyalty_points))
        batch_quantity = Quantity.objects.filter(
            batch_id=sold_product.id).first()

        batch_quantity.quantity_remaining -= product_detail.quantity
        batch_quantity.save()
        product_quantity = product_detail.quantity
        batch_quantity_history = batch_history(
            batch_info=sold_product, sale=sale, product=sold_product.product,
            quantity_taken=product_quantity)
        batch_quantity_history.save()

        detail = sale_detail(quantity=product_detail.quantity,
                             discount=product_detail.discount,
                             price=product_detail.price,
                             note=product_detail.note,
                             product=sold_product.product,
                             sale=sale)
        sale_details.append(detail)

    sale_detail.objects.bulk_create(sale_details)
    return sum(sold_products_loyalty_points)
