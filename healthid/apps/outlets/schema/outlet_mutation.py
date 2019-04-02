import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.outlets.models import Outlet
from healthid.apps.outlets.schema.outlet_schema import OutletType


class CreateOutlet(graphene.Mutation):
    """
    Creates an outlet
    """
    outlet = graphene.Field(OutletType)

    class Arguments:
        name = graphene.String()
        kind_id = graphene.Int()
        address_line1 = graphene.String()
        address_line2 = graphene.String()
        lga = graphene.String()
        city_id = graphene.Int()
        phone_number = graphene.String()
        date_launched = graphene.types.datetime.Date()
        prefix_id = graphene.String()
        business_id = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            outlet = Outlet()
            for(key, value) in kwargs.items():
                setattr(outlet, key, value)
            outlet.save()
        except Exception as e:
            raise Exception(f'Something went wrong {e}')

        return CreateOutlet(
            outlet=outlet
        )


class UpdateOutlet(graphene.Mutation):
    """
    Updates an outlet
    """
    outlet = graphene.Field(OutletType)

    class Arguments:
        id = graphene.Int()
        name = graphene.String()
        address_line1 = graphene.String()
        address_line2 = graphene.String()
        phone_number = graphene.String()
        lga = graphene.String()
        date_launched = graphene.String()
        prefix_id = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        outlet = Outlet.objects.get(pk=id)
        for(key, value) in kwargs.items():
            if key is not None:
                setattr(outlet, key, value)
        outlet.save()

        return UpdateOutlet(
            outlet=outlet
        )


class DeleteOutlet(graphene.Mutation):
    """
    Deletes an outlet
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @master_admin_required
    def mutate(self, info, id):
        outlet = Outlet.objects.get(pk=id)
        outlet.delete()

        return DeleteOutlet(
            success="Outlet has been deleted"
        )


class Mutation(graphene.ObjectType):
    create_outlet = CreateOutlet.Field()
    delete_outlet = DeleteOutlet.Field()
    update_outlet = UpdateOutlet.Field()
