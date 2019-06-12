from django.core.validators import RegexValidator, EmailValidator
from django.db.models import Q

import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from graphene.utils.resolve_only_args import resolve_only_args
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.profiles.models import Profile
from healthid.utils.app_utils.database import get_model_object


class CustomerCustomerType(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'id': ['exact'],
            'first_name': ['iexact', 'icontains', 'istartswith'],
            'last_name': ['iexact', 'icontains', 'istartswith'],
            'primary_mobile_number': ['exact'],
            'secondary_mobile_number': ['exact'],
            'email': ['iexact'],
            'city_id': ['exact'],
            'local_government_area': ['iexact'],
            'loyalty_member': ['exact']
        }

        interfaces = (graphene.relay.Node, )

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class Query(graphene.AbstractType):
    """
    Queries Customer
    Args:
        name (str) any of the customer's name
        mobile_number (str) any of the customers mobile number
        # Arguments when filtering
        customer_id (str) the customer's unique identifier
        first_name (str) the customer's first name
        last_name (str) the customer's last name
        primary_mobile_number (str) the customer's primary mobile number
        secondary_mobile_number (str) the customer's secondary mobile number
        email (email) the customers email
        local_government_area (str) the customers lga
        city_id (int) foreign key, city of the customer
        loyalty_member (bool)
    returns:
         customer(s) object where one or more results were found,
         otherwise a GraphqlError is raised
    """

    customers = graphene.List(CustomerCustomerType)
    customer = graphene.Field(
        lambda: graphene.List(
            CustomerCustomerType),
        name=graphene.String(),
        mobile_number=graphene.String(),
        customer_id=graphene.String())
    filter_customers = DjangoFilterConnectionField(CustomerCustomerType)

    @login_required
    def resolve_customers(self, info, **kwargs):
        resolved_value = Profile.objects.all()
        return resolved_value

    @login_required
    def resolve_customer(self, info, **kwargs):
        name = kwargs.get('name')
        mobile_number = kwargs.get('mobile_number')
        customer_id = kwargs.get('customer_id')

        if name:
            resolved_value = Profile.objects.filter(
                Q(first_name__iexact=name) | Q(
                    last_name__iexact=name))
            if not resolved_value:
                raise GraphQLError(
                    'No customers found matching the name {}'.format(name))
            return resolved_value

        if mobile_number:
            resolved_value = Profile.objects.filter(
                Q(primary_mobile_number=mobile_number) |
                Q(secondary_mobile_number=mobile_number))
            if not resolved_value:
                raise GraphQLError(
                    'No customers found matching'
                    ' the mobile number {}'.format(mobile_number))
            return resolved_value

        if customer_id:
            resolved_value = get_model_object(Profile, 'id', customer_id)
            return (resolved_value,)

        return None

    @login_required
    def resolve_filter_customers(self, info, **kwargs):
        for key in kwargs:
            if key == 'email__iexact':
                EmailValidator(
                    message='Please provide a valid email')(
                    kwargs[key])
            else:
                RegexValidator(
                    r"^[0-9a-zA-Z\']+$",
                    "Please provide a valid search keyword."
                    " Only letters, numbers, and apostrophes allowed")(
                    kwargs[key])

        resolved_value = Profile.objects.filter(
            **kwargs).order_by('first_name')

        if not resolved_value:
            queries = ', '.join(list(kwargs.values()))
            raise GraphQLError(
                'Customer matching the search'
                ' parameters ({}) does not exist'.format(queries))
        return resolved_value
