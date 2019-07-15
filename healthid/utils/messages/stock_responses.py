STOCK_SUCCESS_RESPONSES = {
    "stock_transfer_open_success": "Stock Transfer opened successfully!",
    "stock_transfer_close_success": "Stock transfer closed successfully!",
    "stock_approval_success": "Stock Count has been sent for approval",
    "stock_count_delete_success": "Stock Count with id {stock_count.id} "
                                  "has been deleted",
    "stock_count_template_cancel": "Stock counts template canceled",
    "stock_account_save_in_progress": "Stock Count has been saved in progress",
    "batch_deletion_success": "{}, Batch Deleted from stock count",
    "variance_reason": "Specify the variance reason"
}

STOCK_ERROR_RESPONSES = {
    "invalid_count_field": "Stock Count id field can't be empty",
    "inexistent_batch_error": "Batch with ids '{}' do not exist "
                              "in this stock count.",
    "duplication_approval": "Stock count is already approved.",
    "inexistent_stock_transfer": "That stock transfer does not exist!",
    "outlet_transfer_validation": "You can't open a transfer "
                                  "to your own outlet!",
    "close_transfer_error": "You don't have transfers to close!",
    "product_template_error": "Product must belong to this stock template",
    "product_batch_id_error": "does not have batches with id {}",
    "batch_count_error": "Stock must contain at least (one) 1 batch",
    "zero_stock_transfers": "No stock transfers yet!",
    "variance_error": "There is a variance, Kindly state the variance reason",
    "inexistent_batch_id": "Please provide atleast one batch id."
}
