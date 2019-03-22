import graphene
import graphql_jwt

from healthid.apps.authentication.schema import (AuthMutation, AuthQuery,
                                         ObtainJSONWebToken)
from healthid.apps.business.schema import business_mutation, business_query


class Query(AuthQuery, business_query.Query, graphene.ObjectType):
    pass


class Mutation(AuthMutation, business_mutation.Mutation, graphene.ObjectType):
    # Add Mutations provided by graphql_jwt to generate
    # and verify tokens
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
