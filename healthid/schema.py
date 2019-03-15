import graphene
from .apps.authentication.schema import Mutation


class Mutations(Mutation):
    pass

schema = graphene.Schema(mutation=Mutations)
