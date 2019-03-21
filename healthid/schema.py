from healthid.apps.authentication.schema import Mutation, Query, ObtainJSONWebToken
from healthid.apps.authentication.auth_schema import auth_queries
from healthid.apps.authentication.auth_schema import auth_mutations
import graphene
import graphql_jwt


class Query(Query, auth_queries.Query, graphene.ObjectType):
    pass


class Mutation(Mutation, auth_mutations.Mutation, graphene.ObjectType):
    # Add Mutations provided by graphql_jwt to generate
    # and verify tokens
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
