import re
from graphql import GraphQLError


class ValidateFields:
    """This class validates a name field, an error
    is raised if a name contains special characters
    """

    def validate_name(self, name, city_country):
        regex = re.compile(r'[@_!#$%^&*()<>?/\|}{~:]')
        if(regex.search(name) is not None) or len(name.strip()) < 1:
            raise GraphQLError(
                f'Invalid {city_country} name, cannot'
                ' contain special charaters or be blank')
        return name


validate_fields = ValidateFields()
