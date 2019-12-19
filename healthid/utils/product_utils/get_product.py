from rest_framework.exceptions import ValidationError


def get_product(user_bussinesses, products,
                searched_product, row_count):
    current_product = None
    for user_business in user_bussinesses:
        for product in products:
            if product.get('business_id') == user_business.get('id'):
                current_product = product
                break
        if current_product:
            break
    if not current_product:
        raise ValidationError({
            'error': "This product '{}' does not exist on row {}"
            .format(searched_product, row_count)
        })
    return current_product
