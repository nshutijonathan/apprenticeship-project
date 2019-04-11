import graphene
from django.db import IntegrityError
from graphql import GraphQLError
from django.db.models import Q
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.outlets.models import City, Country, Outlet
from healthid.apps.outlets.schema.outlet_schema import (
    CityType,
    CountryType,
    OutletType
)
from healthid.apps.utils.outlets.check_citie import CheckCity
from healthid.apps.utils.outlets.validators import validate_fields


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


class CreateCountry(graphene.Mutation):
    """
    Creates country
    """
    country = graphene.Field(CountryType)

    class Arguments:
        name = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        name = kwargs.get('name').strip().title()
        name = validate_fields.validate_name(name, 'Country')
        try:
            country = Country.objects.create(name=name)
        except IntegrityError:
            raise GraphQLError(
                f'The country with country name {name} already exists')
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
    @master_admin_required
    def mutate(self, info, **kwargs):
        country_id = kwargs.get('country_id', '')
        city_name = kwargs.get('city_name', '')
        city_name = validate_fields.validate_name(city_name, 'city')
        city_name = city_name.title()
        try:
            country = Country.objects.get(id=country_id)
            if CheckCity.check_city(city_name, country_id)[0]:
                raise GraphQLError(f'City {city_name} already exists')
            city = City.objects.create(name=city_name, country=country)
        except Country.DoesNotExist:
            raise GraphQLError('The country you selected doesnot exist')
        return CreateCity(
            city=city
        )


class EditCountry(graphene.Mutation):
    """Edit a country
    """
    country = graphene.Field(CountryType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()
        name = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name', '').strip().title()
        name = validate_fields.validate_name(name, 'country')

        country_check = Country.objects.filter(name=name).first()
        if country_check:
            raise GraphQLError(f'The country {name} already exists')

        try:
            country = Country.objects.get(id=id)
            country.name = name
            country.save()
            success = "Country successfully updated"
        except Country.DoesNotExist:
            raise GraphQLError(f'The country with Id {id} does not exist')
        return EditCountry(
            country=country, success=success
        )


class EditCity(graphene.Mutation):
    """Edit country
    """
    city = graphene.Field(CityType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name', '').strip().title()
        name = validate_fields.validate_name(name, 'city')
        city = City.objects.filter(Q(name=name) | Q(id=id)).first()
        if city:
            if city.name == name:
                raise GraphQLError(f'The city {name} already exists')
            city.name = name
            city.save()
            success = "City successfully updated"
            return EditCity(city=city, success=success)
        raise GraphQLError(f'The city with Id {id} doesnot exist')


class DeleteCountry(graphene.Mutation):
    """Delete a country
    """
    country = graphene.Field(CountryType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        try:
            country = Country.objects.get(pk=id)
            country.delete()
            success = 'Country was successfully deleted'
        except Country.DoesNotExist:
            raise GraphQLError(f'The country with Id {id} doesnot exist')
        return DeleteCountry(
            success=success
        )


class Mutation(graphene.ObjectType):
    create_outlet = CreateOutlet.Field()
    delete_outlet = DeleteOutlet.Field()
    update_outlet = UpdateOutlet.Field()
    create_city = CreateCity.Field()
    create_country = CreateCountry.Field()
    edit_country = EditCountry.Field()
    delete_country = DeleteCountry.Field()
    edit_city = EditCity.Field()
