import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import Role
from healthid.apps.outlets.models import \
    City, Country, Outlet, OutletUser
from healthid.apps.outlets.schema.outlet_schema import (CityType, CountryType,
                                                        OutletType,
                                                        OutletMetaType,
                                                        OutletContactsType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.outlet_utils.validators import validate_fields
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES
from healthid.apps.authentication.schema.queries.auth_queries import UserType
from healthid.utils.app_utils.check_user_in_outlet import \
    get_user_active_outlet
from healthid.utils.outlet_utils.metadata_handler import \
    add_outlet_metadata, update_outlet_metadata


class CreateOutlet(graphene.Mutation):
    """
    Creates an outlet
    """
    outlet = graphene.Field(OutletType)
    outlet_meta = graphene.Field(OutletMetaType)
    outlet_contacts = graphene.Field(OutletContactsType)
    success = graphene.String()

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
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet_name = kwargs.get('name')
        business_id = kwargs.get('business_id')
        find_outlets = \
            Outlet.objects.filter(name=outlet_name)

        for outlet in find_outlets:
            if business_id == outlet.business_id:
                raise GraphQLError('This business already has'
                                   ' an outlet with that name')

        outlet = Outlet()
        for(key, value) in kwargs.items():
            setattr(outlet, key, value)
        role_instance = get_model_object(Role, 'id', user.role_id)
        with SaveContextManager(outlet, model=Outlet) as outlet:
            add_outlet_metadata(outlet, kwargs.items())
            OutletUser.objects.create(
                user=user, outlet=outlet, is_active_outlet=True,
                role=role_instance)
            return CreateOutlet(
                outlet=outlet,
                success=SUCCESS_RESPONSES["creation_success"].format("Outlet")
            )


class UpdateOutlet(graphene.Mutation):
    """
    Updates an outlet
    """
    outlet = graphene.Field(OutletType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        address_line1 = graphene.String()
        address_line2 = graphene.String()
        phone_number = graphene.String()
        lga = graphene.String()
        date_launched = graphene.types.datetime.Date()
        prefix_id = graphene.String()
        preference_id = graphene.String()
        kind_id = graphene.Int()
        city_id = graphene.Int()
        role_id = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet_id = kwargs.get('id')
        outlet = get_user_active_outlet(user, outlet_id=outlet_id)
        for(key, value) in kwargs.items():
            setattr(outlet, key, value)
        update_outlet_metadata(outlet, kwargs.items())
        success = SUCCESS_RESPONSES["update_success"].format(outlet.name)
        return UpdateOutlet(outlet=outlet, success=success)


class DeleteOutlet(graphene.Mutation):
    """
    Deletes an outlet
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        outlet = get_model_object(Outlet, 'id', id)
        outlet.delete(user)
        return DeleteOutlet(
            success=SUCCESS_RESPONSES["deletion_success"].format("Outlet"))


class CreateCountry(graphene.Mutation):
    """
    Creates country
    """
    country = graphene.Field(CountryType)

    class Arguments:
        name = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        name = kwargs.get('name').strip().title()
        name = validate_fields.validate_name(name, 'Country')
        country = Country(name=name)
        with SaveContextManager(country, model=Country) as country:
            return CreateCountry(country=country)


class CreateCity(graphene.Mutation):

    """
    Creates a city
    """
    city = graphene.Field(CityType)

    class Arguments:
        city_name = graphene.String()
        country_id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        country_id = kwargs.get('country_id', '')
        city_name = kwargs.get('city_name', '')
        city_name = validate_fields.validate_name(city_name, 'city')
        city_name = city_name.title()
        country = get_model_object(Country, 'id', country_id)
        cities = [city['name'] for city in list(country.city_set.values())]
        if city_name in cities:
            raise GraphQLError(
                OUTLET_ERROR_RESPONSES[
                    "city_double_creation_error"].format(
                    "City " + city_name))
        city = City(name=city_name, country=country)
        with SaveContextManager(city, model=City):
            return CreateCity(city=city)


class EditCountry(graphene.Mutation):
    """Edit a country
    """
    country = graphene.Field(CountryType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()
        name = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name', '').strip().title()
        name = validate_fields.validate_name(name, 'country')
        country = get_model_object(Country, 'id', id)
        country.name = name
        with SaveContextManager(country, model=Country):
            success = SUCCESS_RESPONSES["update_success"].format("Country")
            return EditCountry(country=country, success=success)


class EditCity(graphene.Mutation):
    """Edit country
    """
    city = graphene.Field(CityType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name', '').strip().title()
        name = validate_fields.validate_name(name, 'city')
        city = get_model_object(City, 'id', id)
        country_cities = City.objects.filter(country=city.country).all()
        if name in [str(city) in country_cities]:
            raise GraphQLError(OUTLET_ERROR_RESPONSES[
                "city_double_creation_error"].format(
                "The city " + name))
        city.name = name
        city.save()
        return EditCity(city=city,
                        success=SUCCESS_RESPONSES[
                            "update_success"].format("City"))


class DeleteCountry(graphene.Mutation):
    """Delete a country
    """
    country = graphene.Field(CountryType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        country = get_model_object(Country, 'id', id)
        country.delete(user)
        return DeleteCountry(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Country"))


class ActivateDeactivateOutletUser(graphene.Mutation):
    """
    Mutataion to activate or deactivate user from an outlet

    Attributes:
        outlet_id(int): id for outlet whose user you want to activate or
                        deactivate
        user_id(string): id for user  to activate or deactivate in
                         outlet
        is_active(boolean): True if you want to activate a user
                            otherwise False to deactivate

    Returns:
        message(string): indicating user has been activated or
                         deactivated
        user(obj): user who has been activated or deactivated
    """
    user = graphene.Field(UserType)
    message = graphene.String()

    class Arguments:
        outlet_id = graphene.Int(required=True)
        user_id = graphene.String(required=True)
        is_active = graphene.Boolean(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        outlet_user, message = outlet.activate_deactivate_user(
            info.context.user, **kwargs)
        return ActivateDeactivateOutletUser(message=message, user=outlet_user)


class Mutation(graphene.ObjectType):
    create_outlet = CreateOutlet.Field()
    delete_outlet = DeleteOutlet.Field()
    update_outlet = UpdateOutlet.Field()
    create_city = CreateCity.Field()
    create_country = CreateCountry.Field()
    edit_country = EditCountry.Field()
    delete_country = DeleteCountry.Field()
    edit_city = EditCity.Field()
    activate_deactivate_outlet_user = ActivateDeactivateOutletUser.Field()
