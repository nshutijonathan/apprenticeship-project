from healthid.apps.outlets.models import City, Country, Outlet, OutletKind
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.outlets import (create_outlet, delete_outlet,
                                                  update_outlet)


class OutletTestCase(BaseConfiguration):
    def test_empty_db(self):
        resp = self.query_with_token(
            self.access_token_master,
            '{outlets{id}}')
        self.assertNotEquals(resp, {'outlets': []})

    def test_single_outlet(self):
        outlet = self.outlet
        query_string = "{outlet(id:" + str(outlet.id) + "){id}}"
        resp = self.query_with_token(self.access_token_master, query_string)
        self.assertResponseNoErrors(resp, {"outlet": {"id": str(outlet.id)}})

    def test_create_outlet(self):
        info = self.outlet_kind
        response = self.query_with_token(
            self.access_token_master,
            create_outlet(
                self.business.id,
                info['city_id'],
                info["outlet_kindid"]),
        )
        self.assertResponseNoErrors(
            response, {"createOutlet": {
                'outlet': {'name': 'green ville'}
            }})

    def test_update_outlet(self):
        outlet = self.outlet
        outlet.user.add(self.master_admin_user)
        response = self.query_with_token(
            self.access_token_master,
            update_outlet(outlet.id,
                          str(outlet.name)),
        )
        self.assertResponseNoErrors(
            response, {"updateOutlet": {
                'outlet': {'name': str(outlet.name),
                           'prefixId': outlet.prefix_id}
            }})

    def test_outlet_model(self):
        all_outlets = Outlet.objects.all()
        self.assertGreater(len(all_outlets), 0)

    def test_country_model(self):
        Country.objects.create(name="Kenya")
        all_countries = Country.objects.all()
        self.assertGreater(len(all_countries), 0)

    def test_city_model(self):
        country = Country.objects.create(name='Kenya')
        City.objects.create(name='Nairobi', country_id=country.id)
        all_cities = City.objects.all()
        self.assertGreater(len(all_cities), 0)

    def test_outletkind_model(self):
        OutletKind.objects.create(name='storefront')
        all_types = OutletKind.objects.all()
        self.assertGreater(len(all_types), 0)

    def test_delete_outlet(self):
        outlet = self.outlet
        response = self.query_with_token(
            self.access_token_master,
            delete_outlet(outlet.id))
        self.assertIn("success", response["data"]["deleteOutlet"])
