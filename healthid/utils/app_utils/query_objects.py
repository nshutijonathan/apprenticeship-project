
from functools import reduce

from django.db.models import Q
from graphql import GraphQLError


class GetObjectList:
    error = 'Cannot query an empty list of object IDs'

    @staticmethod
    def get_objects(model, list_of_ids, message=None):
        """Queries the database to return a list of
        objects

        Arguments:
            list of products ids
            model name

        Returns:
            A list of objetcs
        """
        if not list_of_ids:
            message = message or GetObjectList.error
            raise GraphQLError(message)
        query = reduce(lambda q, id: q | Q(id=id), list_of_ids, Q())
        queryset = model.objects.filter(query)
        if not queryset:
            ids = ', '.join(map(str, list_of_ids))
            raise GraphQLError(
                f'There are no {model.__name__}(s) matching IDs: {ids}.')
        return queryset
