CONSULTATION_SUCCESS_RESPONSES = {
    "consultation_schedule_success": "Consultation has been scheduled",
    "delete_booking": "Consultation for {} deleted successfully"
}

CONSULTATION_ERROR_RESPONSES = {
    "empty_field_error": "The {} field can't be empty",
    "duplicate_consultation_error": "Consultation with "
                                    "consultation_name {}, already exists",
    "inexistent_outlet": "Outlet with id {} does not exist",
    "booking_date_error":
    "Booking date cannot be earlier than present date and time",
    "paid_status_error":
    "Consultation cannot be marked as paid if it does not have \
     a sale record attached to it",
    "completed_status_error": "Consultation is already marked as complete"
}
