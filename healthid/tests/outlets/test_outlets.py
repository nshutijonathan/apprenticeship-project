from healthid.apps.outlets.models import City, Country, Outlet, OutletKind
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.outlets import (create_outlet, delete_outlet,
                                                  update_outlet)
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


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
            self.another_master_admin_token,
            create_outlet(
                self.business.id,
                info["outlet_kindid"],
                "Rwanda",
                "Kigali"),
        )

        self.assertResponseNoErrors(
            response, {"createOutlet": {
                'outlet': {
                    'id': response['data']['createOutlet']['outlet']['id'],
                    'name': 'green ville'
                    }
            }})

    def test_city_not_exist(self):
        info = self.outlet_kind
        response = self.query_with_token(
            self.another_master_admin_token,
            create_outlet(
                self.business.id,
                info["outlet_kindid"],
                "Rwanda",
                "Kig"),
        )
        message = OUTLET_ERROR_RESPONSES["city_not_exist"]
        self.assertIn('errors', response)
        self.assertEqual(message, response['errors'][0]['message'])

    def test_country_not_exist(self):
        info = self.outlet_kind
        response = self.query_with_token(
            self.another_master_admin_token,
            create_outlet(
                self.business.id,
                info["outlet_kindid"],
                "Rwan",
                "Kigali"),
        )
        message = OUTLET_ERROR_RESPONSES["country_not_exist"]
        self.assertIn('errors', response)
        self.assertEqual(message, response['errors'][0]['message'])

    def test_update_outlet(self):
        outlet = self.outlet
        response = self.query_with_token(
            self.access_token_master,
            update_outlet(outlet.id,
                          outlet.name,
                          "Uganda",
                          "Kampala"),
        )
        self.assertResponseNoErrors(
            response, {"updateOutlet": {
                'outlet': {'name': outlet.name}
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
