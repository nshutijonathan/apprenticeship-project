from graphql import GraphQLError

from healthid.utils.app_utils.validators import validate_email


class ValidateBusiness:
    '''Class to validate the business attributes
    '''

    def validate_business(self, **business_fields):
        '''Method to validate the business attributes
        '''
        validate_email(business_fields['business_email'])
        if not (business_fields['trading_name'] and
                business_fields['legal_name']):
            raise GraphQLError(
                'Both trading name and legal name are required!')
        elif not business_fields['phone_number']:
            raise GraphQLError('Phone number is required!')
        elif not business_fields['city'] and business_fields['country']:
            raise GraphQLError('Both city and country are required!')
        elif not business_fields['address_line_1']:
            raise GraphQLError('Address Line 1 is required!')
