import math


def initiate_sale(sold_product_instances, sold_products, sale, sale_detail):
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
        product_category = sold_product.product_category
        loyalty_points = (product_detail.price / product_category.amount_paid) * sold_product.loyalty_weight  # noqa
        sold_products_loyalty_points.append(math.floor(loyalty_points))
        batches = sold_product.batch_info.filter(
            batch_quantities__quantity_received__gt=0).order_by('expiry_date')
        product_quantity = product_detail.quantity
        for batch in batches:
            batch_quantity = batch.quantity
            quantity = batch.batch_quantities.filter(is_approved=True).first()
            if product_quantity <= batch_quantity:
                quantity.quantity_received = batch_quantity \
                    - product_quantity
                quantity.save()
                break
            else:
                quantity.quantity_received = 0
                quantity.save()
                product_quantity -= batch_quantity

        detail = sale_detail(quantity=product_detail.quantity,
                             discount=product_detail.discount,
                             price=product_detail.price,
                             note=product_detail.note,
                             product=sold_product,
                             sale=sale)
        sale_details.append(detail)

    sale_detail.objects.bulk_create(sale_details)
    return sum(sold_products_loyalty_points)
