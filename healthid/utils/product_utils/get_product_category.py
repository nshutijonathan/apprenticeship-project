from rest_framework.exceptions import ValidationError


def get_product_category(user_outlets, product_categories,
                         searched_category, row_count):
    product_category = None
    for user_outlet in user_outlets:
        for category in product_categories:
            if category.get('outlet_id') == user_outlet.get('outlet_id'):
                product_category = category
                break
        if product_category:
            break
    if not product_category:
        raise ValidationError({
            'error': "This category '{}' does not exist on row {}"
            .format(searched_category, row_count)
        })
    return product_category
