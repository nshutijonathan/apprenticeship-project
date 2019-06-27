import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import City, Country, Outlet
from healthid.apps.outlets.schema.outlet_schema import (CityType, CountryType,
                                                        OutletType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.outlet_utils.validators import validate_fields


class CreateOutlet(graphene.Mutation):
    """
    Creates an outlet
    """
    outlet = graphene.Field(OutletType)
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
        with SaveContextManager(outlet, model=Outlet) as outlet:
            outlet.user.add(user)
            return CreateOutlet(
                outlet=outlet, success="Outlet created successfully"
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

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        outlet = get_model_object(Outlet, 'id', id)
        outlet_users = outlet.user.all()
        if user not in outlet_users:
            raise GraphQLError(
                "You can't update an outlet that you are not assigned to!")
        for(key, value) in kwargs.items():
            setattr(outlet, key, value)
        with SaveContextManager(outlet, model=Outlet) as outlet:
            success = f'Successfully updated outlet {outlet.name}'
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
        return DeleteOutlet(success="Outlet has been deleted")


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
            raise GraphQLError(f'City {city_name} already exists')
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
            success = "Country successfully updated"
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
            raise GraphQLError(f'The city {name} already exists')
        city.name = name
        city.save()
        return EditCity(city=city, success='City successfully updated')


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
        return DeleteCountry(success='Country was successfully deleted')


class Mutation(graphene.ObjectType):
    create_outlet = CreateOutlet.Field()
    delete_outlet = DeleteOutlet.Field()
    update_outlet = UpdateOutlet.Field()
    create_city = CreateCity.Field()
    create_country = CreateCountry.Field()
    edit_country = EditCountry.Field()
    delete_country = DeleteCountry.Field()
    edit_city = EditCity.Field()
