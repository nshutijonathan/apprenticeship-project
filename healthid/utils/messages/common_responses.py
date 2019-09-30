SUCCESS_RESPONSES = {
    "creation_success": "{}, created successfully!",
    "with_interval": "{}, scheduled successfully!",
    "update_success": "{}, updated successfully!",
    "deletion_success": "{}, deleted successfully!",
    "approval_success": "{}, approved successfully!",
    "edit_success": "{}, edited successfully!",
    "upload_success": "{}, uploaded successfully!",

}

ERROR_RESPONSES = {
    "inexistent_record_query_error": "{} record does not exist",
    "invalid_field_error": "Please input a valid {}",
    "empty_field_error": "{} cannot be empty",
    "required_field": "{} is required!",
    "duplication_error": "{}, already exists!",
    "authorization_error": "You do not have permission to perform this action",
    "invalid_login_credentials": "Please, enter valid credentials",
    "invalid_date_format": "Incorrect data format for {}, "
                           "should be YYYY-MM-DD",
    "update_error": "You can't update a business,you're not assigned to!",
    "no_matching_ids": "There are no {}(s) matching IDs: {}.",
    "invalid_id": "The id {} should be a positive number starting from 1 or"
    " just a string of characters",
    "invalid_values": "{} contains invalid values",
    "wrong_param": "Please provide a valid parameter in the url",
    "csv_missing_field": "csv file is missing some column(s)",
    "csv_many_field": "csv file has more than the required column(s)"
}
