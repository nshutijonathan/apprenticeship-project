import graphene
import graphql_jwt

from healthid.apps.authentication.schema import (AuthMutation, AuthQuery,
                                                 ObtainJSONWebToken)
from healthid.apps.business.schema import business_mutation, business_query
from healthid.apps.orders.schema import SuppliersMutation, SuppliersQuery
from healthid.apps.outlets.schema import outlet_mutation, outlet_schema


class Query(
        AuthQuery,
        business_query.Query,
        outlet_schema.Query,
        SuppliersQuery,
        graphene.ObjectType):
    pass


class Mutation(
        AuthMutation,
        business_mutation.Mutation,
        outlet_mutation.Mutation,
        SuppliersMutation,
        graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
