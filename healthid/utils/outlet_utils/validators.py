import re
from graphql import GraphQLError
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


class ValidateFields:
    """This class validates a name field, an error
    is raised if a name contains special characters
    """

    def validate_name(self, name, city_country):
        regex = re.compile(r'[@_!#$%^&*()<>?/\|}{~:]')
        if(regex.search(name) is not None) or len(name.strip()) < 1:
            raise GraphQLError(
                OUTLET_ERROR_RESPONSES[
                    "invalid_city_or_country_name"].format(city_country))
        return name


validate_fields = ValidateFields()
