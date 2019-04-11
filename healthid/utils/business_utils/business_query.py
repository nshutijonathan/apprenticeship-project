from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
from healthid.apps.business.models import Business
from healthid.apps.outlets.models import Outlet


class BusinessModelQuery:
    """
    this class create queries for the role
    """

    def query_business_id(self, id):
        try:
            business = Business.objects.get(id=id)
            return business
        except ObjectDoesNotExist:
            raise GraphQLError(f"Business with { id } id does not exist.")

    def query_business_name(self, name):
        try:
            business = Business.objects.get(name=name)
            return business
        except ObjectDoesNotExist:
            raise GraphQLError(f"Business with { name } name does not exist.")

    def query_outlet_id(self, id):
        try:
            outlet = Outlet.objects.get(id=id)
            return outlet
        except ObjectDoesNotExist:
            raise GraphQLError(f"Outlet with { id } id does not exist.")
