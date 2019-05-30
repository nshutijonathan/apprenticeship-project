import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.outlets.models import City, Country
from healthid.apps.customers.schema.customer_schema import (
                                                        CustomerProfileType)
from healthid.apps.profiles.models import Profile
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.customer_utils.create_customer_validation \
     import (validate_customer_fields)


class CreateCustomer(graphene.Mutation):
    """
    Creates a Customer


    Args:
        first_name (str) the customers first name
        last_name (str) the customers last name
        primary_mobile_number (str) the customers mobile number
        secondary_mobile_number = (str) the customers mobile number 2
        email (email) the customers email
        address_line_1 (str) the customers address 1
        address_line_2 (str) the customers address 2
        local_government_area (str) the customers lga
        city_id (int) foreign key, city of the customer
        country_id (int) foreign key, country of the customer
        emergency_contact_name (Str) customer emergency contact name
        emergency_contact_number (Str) customer emergency contact mobile number
        emergency_contact_email (email) customer emergency contact email
        loyalty_member (bool)

    returns:
         success message and details of customer created if successful,
         otherwise a GraphqlError is raised
    """
    customer = graphene.Field(CustomerProfileType)
    message = graphene.String()

    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        primary_mobile_number = graphene.String(required=True)
        secondary_mobile_number = graphene.String(required=True)
        email = graphene.String(required=True)
        address_line_1 = graphene.String()
        address_line_2 = graphene.String()
        local_government_area = graphene.String()
        city_id = graphene.Int(required=True)
        country_id = graphene.Int(required=True)
        emergency_contact_name = graphene.String(required=True)
        emergency_contact_number = graphene.String(required=True)
        emergency_contact_email = graphene.String(required=True)
        loyalty_member = graphene.Boolean(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        get_model_object(City, 'id', kwargs.get("city_id"))
        get_model_object(Country, 'id', kwargs.get("country_id"))
        customer = Profile()
        customer = validate_customer_fields(customer, **kwargs)
        customer_found = Profile.objects.filter(
            primary_mobile_number=kwargs['primary_mobile_number'])

        if customer_found:
            raise GraphQLError(
                          'Customer with primary mobile number {} already \
exists!'.format(kwargs["primary_mobile_number"]))
        params = {'model_name': 'Profile',
                  'field': 'email', 'value': customer.email}
        with SaveContextManager(customer, **params) as customer:
            return CreateCustomer(
                       message="Customer Created successfully",
                       customer=customer)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
