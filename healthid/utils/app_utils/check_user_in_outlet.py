from graphql import GraphQLError
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.outlets.models import Outlet


def check_user_belongs_to_outlet(user, outlet_id):
    outlet = get_model_object(Outlet, 'id', outlet_id)
    if user not in outlet.user.all():
        raise GraphQLError(
            f'You don\'t belong to outlet with id {outlet_id}.'
        )
    return outlet
