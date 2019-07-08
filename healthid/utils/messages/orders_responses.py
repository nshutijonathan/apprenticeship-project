ORDERS_SUCCESS_RESPONSES = {
    "scan_save_success": "Scan successfully saved",
    "invoice_upload_success": "Invoice uploaded successfully",
    "order_initiation_success": "Order successfully initiated!",
    "order_addition_success": "Successfully added order details!",
    "supplier_approval_success": "supplier {} has been approved!",
    "supplier_deletion_success": "supplier {} has been deleted!",
    "supplier_edit_request_success": "Edit request for Supplier {}"
                                     "has been sent!",
    "supplier_edit_request_update_success": "Edit request for Supplier {} "
                                            "has been updated!",
    "supplier_update_success": "Supplier {} has been successfully updated!",

}

ORDERS_ERROR_RESPONSES = {
    "duplicate_upload_error": "An invoice for this order already exists",
    "initiation_invoice_upload_error": "Cannot upload Invoice. Your outlet "
                                       "did not initiate this order",
    "supplier_edit_proposal_validation_error": "You can only propose an edit "
                                               "to an approved supplier!",
    "edit_proposal_validation_error": "You can't edit an edit request "
                                      "you did not propose!",
    "supplier_note_length_error": "Suppliers note must be two or more words",
    "supplier_note_update_validation_error": "You can't update a note you "
                                             "didn't create",
    "supplier_note_deletion_validation_error": "You can't delete a note "
                                               "you didn't create",
    "supplier_search_key_error": "Please provide a valid search keyword",
    "inexistent_supplier_search_error": "Supplier matching query"
                                        "does not exist!",
    "supplier_request_denied": "Edit request for supplier {}"
                               "has been declined!",
    "scan_order_rejection": "Scan rejected: this order"
                            " is not marked closed.",
    "scan_batch_rejection": "Scan rejected: BatchInfo does"
                            " not match the provided outlet",
    "scan_product_rejection": "Scan rejected: Product does"
                              " not match the provided BatchInfo"

}
