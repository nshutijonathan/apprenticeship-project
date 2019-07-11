import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.sales.sales_velocity import SalesVelocity


class Velocity(graphene.ObjectType):
    default_sales_velocity = graphene.Float()
    calculated_sales_velocity = graphene.Float()
    message = graphene.String()


class Query(graphene.ObjectType):
    """
    Queries Sales
    Args:
        product_id (int) the product id
        outlet_id (int) the outlet id
    returns:
        Two float values for the calculated sales velocity
            and the default sales velocity
    """

    sales_velocity = graphene.Field(
        Velocity,
        product_id=graphene.Int(),
        outlet_id=graphene.Int())

    @login_required
    def resolve_sales_velocity(self, info, **kwargs):
        product_id = kwargs.get('product_id')
        outlet_id = kwargs.get('outlet_id')

        return SalesVelocity(
            product_id=product_id,
            outlet_id=outlet_id).velocity_calculator()
