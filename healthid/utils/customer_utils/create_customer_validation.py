from graphql import GraphQLError
from healthid.utils.auth_utils.validations import ValidateUser
from healthid.utils.app_utils.validators import (special_cahracter_validation,
                                                 validate_email)
from healthid.utils.messages.customer_responses import CUSTOMER_ERROR_RESPONSES


def validate_customer_fields(customer, **kwargs):
    """
       Customer Validation, This method takes in instance of customer model
       and kwargs, its validate user inputs, like email, firstname
       phone number, special character etc and raise a Graphql if a condition
       is not being met

    Args:
        Profile() instance
        kwargs

    returns:
         customer instance
         otherwise a GraphqlError is raised
    """
    fields_to_validate = ["first_name", "last_name",
                          "emergency_contact_name",
                          "local_government_area", "address_line_1",
                          "address_line_2"]
    numbers_to_validate = ["primary_mobile_number",
                           "secondary_mobile_number",
                           "emergency_contact_number"]
    emails_to_validate = ["email", "emergency_contact_email"]
    for key, value in kwargs.items():
        if key in fields_to_validate:
            special_cahracter_validation(value)
            if value.strip() == "":
                raise GraphQLError(CUSTOMER_ERROR_RESPONSES[
                                   "first_name_error"].format(key))
        if key in emails_to_validate:
            validate_email(value)
        if key in numbers_to_validate:
            ValidateUser().validate_mobile_number(value)
        setattr(customer, key, value)
    return customer
