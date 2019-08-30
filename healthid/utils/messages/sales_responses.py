SALES_SUCCESS_RESPONSES = {
    "promotion_approval_success": "Promotion has been approved",
    "sales_prompt_create_success": "Successfully created {sales_prompt_count} "
                                   "sales prompt",
    "add_to_cart_success": "Product added to cart.",
    "calculated_velocity":  "Sales velocity calculated successfully."
                            "Use calculated value",
    "sales_return_approved": "Sales return approved successfully"
}

SALES_ERROR_RESPONSES = {
    "outlet_validation_error": "You don\'t belong to outlet "
                               "with this promotion.",
    "promotion_type_error": "Please provide promotion type name.",
    "incomplete_list": "List inputs are incomplete or empty",
    "title_error": "Titles and description must contain words",
    "unapproved_product_error": "{} isn't approved yet.",
    "in_stock_product_error": "There is only quantity "
                              "{} of {} available in stock.",
    "inexistent_promotion": "Promotion with id {} does not exist.",
    "outlet_id_validation_error": "You don't belong to outlet with id {}.",
    "default_velocity": "Not enough sales data to calculate sales velocity."
                        "Please use default value",
    "less_quantities": "Products with ids '{}' do not have enough" +
    " quantities to be sold",
    "negative_integer": "Price for products with ids '{}' should" +
    "be positive integer",
    "negative_discount": "Products with ids '{}' can't have negative discount",
    "not_returnable": "Products with ids {} are not returnable",
    "already_approved_sales_returns":
        "Sales returns with ids {} already approved",
    "empty_sales_return": "Sales return can't be empty!",
    "no_sales_error": "No sales to view yet!",
}
