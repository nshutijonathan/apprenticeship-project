import graphene
import graphql_jwt
from healthid.apps.authentication.schema import (AuthMutation, AuthQuery,
                                                 ObtainJSONWebToken)
from healthid.apps.business.schema import business_mutation, business_query
from healthid.apps.orders.schema import SuppliersMutation, SuppliersQuery
from healthid.apps.outlets.schema import outlet_mutation, outlet_schema
from healthid.apps.preference.schema import (preference_mutation,
                                             preference_schema)
from healthid.apps.products.schema import product_mutations, product_query
from healthid.apps.receipts.schema import receipt_mutation, receipt_schema
from healthid.apps.register.schema import register_mutation, register_schema
from healthid.apps.events.schema import event_querys, event_mutations


class Query(AuthQuery, business_query.Query, outlet_schema.Query,
            preference_schema.Query, SuppliersQuery, receipt_schema.Query,
            register_schema.Query, product_query.Query,
            product_query.BatchQuery, event_querys.Query, graphene.ObjectType):
    pass


class Mutation(AuthMutation, business_mutation.Mutation,
               outlet_mutation.Mutation, preference_mutation.Mutation,
               SuppliersMutation, receipt_mutation.Mutation,
               register_mutation.Mutation, product_mutations.Mutation,
               event_mutations.Mutation, graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
