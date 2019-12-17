import graphene
from graphene_django import DjangoObjectType
from healthid.utils.app_utils.database import get_model_object

from healthid.apps.authentication.models import User
from healthid.apps.outlets.models import Outlet


class ActiveOutletType(DjangoObjectType):
    address_line1 = graphene.String()
    phone_number = graphene.String()
    date_launched = graphene.String()
    address_line2 = graphene.String()
    lga = graphene.String()
    prefix_id = graphene.String()

    class Meta:
        model = Outlet


class UserType(DjangoObjectType):
    active_outlet = graphene.Field(ActiveOutletType)

    class Meta:
        model = User
        exclude_fields = ['password']

    def resolve_active_outlet(self, info, **kwargs):
        """
        get's outlet a user is active in

        Returns:
            obj: outlet user is active in
        """
        if not self.active_outlet:
            return None
        outlet = get_model_object(Outlet, 'id', self.active_outlet.id)
        outlets_meta = outlet.outletmeta_set.all()
        outlets_contact = outlet.outletcontacts_set.all()
        for outlet_meta in outlets_meta:
            if outlet.id == outlet_meta.__dict__['outlet_id']:
                outlet.__dict__[outlet_meta.__dict__[
                    'dataKey']] = outlet_meta.__dict__['dataValue']
            else:
                outlet.__dict__[outlet_meta.__dict__['dataKey']] = None
        for outlet_contact in outlets_contact:
            if outlet.id == outlet_contact.__dict__['outlet_id']:
                outlet.__dict__[outlet_contact.__dict__[
                    'dataKey']] = outlet_contact.__dict__['dataValue']
            else:
                outlet.__dict__[outlet_contact.__dict__['dataKey']] = None

        return outlet
