from healthid.apps.business.tests.utils import create_business
from healthid.apps.outlets.models import City, Country, Outlet, OutletKind
from healthid.tests.outlets.base import OutletBaseTest
from healthid.tests.test_fixtures.outlets import (create_outlet, delete_outlet,
                                                  update_outlet)


class OutletTestCase(OutletBaseTest):
    def test_empty_db(self):
        resp = self.query_with_token(
            self.access_token_master,
            '{outlets{id}}')
        self.assertResponseNoErrors(resp, {'outlets': []})

    def test_single_outlet(self):
        outlet = self.create_outlet()
        query_string = "{outlet(id:" + str(outlet.id) + "){id}}"
        resp = self.query_with_token(self.access_token_master, query_string)
        self.assertResponseNoErrors(resp, {"outlet": {"id": str(outlet.id)}})

    def test_create_outlet(self):
        business = create_business()
        info = self.create_city()
        response = self.query_with_token(
            self.access_token_master,
            create_outlet(business.id, info['city_id'], info["outlet_kindid"]),
        )
        self.assertResponseNoErrors(
            response, {"createOutlet": {
                'outlet': {'name': 'green ville', 'prefixId': 'AN001-GRE'}
            }})

    def test_update_outlet(self):
        outlet = self.create_outlet()
        response = self.query_with_token(
            self.access_token_master,
            update_outlet(outlet.id),
        )
        self.assertResponseNoErrors(
            response, {"updateOutlet": {
                'outlet': {'name': 'green ville', 'prefixId': 'AN005-GRE'}
            }})

    def test_outlet_model(self):
        self.create_outlet()
        all_outlets = Outlet.objects.all()
        self.assertQuerysetEqual(all_outlets, ['<Outlet: bingo>'])

    def test_country_model(self):
        Country.objects.create(name="Kenya")
        all_countries = Country.objects.all()
        self.assertQuerysetEqual(all_countries, ['<Country: Kenya>'])

    def test_city_model(self):
        country = Country.objects.create(name='Kenya')
        City.objects.create(name='Nairobi', country_id=country.id)
        all_cities = City.objects.all()
        self.assertQuerysetEqual(all_cities, ['<City: Nairobi>'])

    def test_outletkind_model(self):
        OutletKind.objects.create(name='storefront')
        all_types = OutletKind.objects.all()
        self.assertQuerysetEqual(all_types, ['<OutletKind: storefront>'])

    def test_delete_outlet(self):
        outlet = self.create_outlet()
        response = self.query_with_token(
            self.access_token_master,
            delete_outlet(outlet.id))
        self.assertIn("success", response["data"]["deleteOutlet"])
