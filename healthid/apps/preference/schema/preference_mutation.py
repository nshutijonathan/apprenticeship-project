import graphene
from graphene_django import DjangoObjectType
from healthid.apps.preference.models import OutletPreference
from graphql_jwt.decorators import login_required


class OutletTypePreference(DjangoObjectType):
    class Meta:
        model = OutletPreference


class UpdateOutletPreference(graphene.Mutation):
    """
    Updates an outlet preference
    """
    preference = graphene.Field(OutletTypePreference)
    success = graphene.String()

    class Arguments:
        outlet_timezone = graphene.String()
        preference_id = graphene.String(required=True)
        outlet_currency = graphene.String()
        outlet_vat = graphene.Float()
        barcode_preference = graphene.Boolean()
        email_preference = graphene.Boolean()
        reorder_point = graphene.Int()
        reorder_max = graphene.Int()
        retain_user = graphene.Boolean()
        sales_hold = graphene.Int()
        sell_inventory_notification = graphene.Boolean()
        payment_method = graphene.String()
        minimum_weeks_for_sales_velocity = graphene.Int()
        sales_velocity = graphene.Int()

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        info = info
        preference = OutletPreference().update_preference(info,
                                                          OutletPreference,
                                                          **kwargs)
        return cls(
                preference=preference,
                success="Preference updated successfully")


class Mutation(graphene.ObjectType):
    update_preference = UpdateOutletPreference.Field()
