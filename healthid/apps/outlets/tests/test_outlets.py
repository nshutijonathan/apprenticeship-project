import json

from django.test import Client, TestCase
from healthid.apps.authentication.models import Role, User
from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.business.models import Business
from healthid.apps.business.tests.utils import create_business
from healthid.apps.outlets.models import City, Country, Outlet, OutletKind


class GraphQLTestCase(TestCase):

    def create_default_role(self):
        return Role.objects.create(name='Master Admin')

    def setUp(self):
        self._client = Client()
        self.user = User.objects.create_user(
            email='you@example.com', password='thisisus', mobile_number='256')
        self.user.is_active = True
        self.user.save()
        self._client.login(email='you@example.com', password='thisisus')

    def query(self, query: str):
        body = {"query": query}
        resp = self._client.post(
            "/healthid/", json.dumps(body), content_type="application/json",)
        jresp = json.loads(resp.content.decode())
        return jresp

    def create_city(self):
        country = Country.objects.create(name='Uganda')
        city = City.objects.create(name="Kampala", country_id=country.id)
        outlet_kind = OutletKind.objects.create(name="Warehouse")
        info = {"city_id": city.id, "outlet_kindid": outlet_kind.id}
        return info

    def create_outlet(self):
        info = self.create_city()
        business = create_business()
        return Outlet.objects.create(
            name="bingo", kind_id=info["outlet_kindid"],
            address_line1="wandegya", phone_number="254745345342",
            address_line2="Central, Kla", lga="KCCA",
            city_id=info["city_id"], date_launched="1995-10-20",
            business_id=business.id)

    def make_user_masteradmin(self):
        self.user.role = self.create_default_role()
        self.user.save()
        self._client.login(email='you@example.com', password='thisisus')

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")

    def test_empty_db(self):
        resp = self.query('{outlets{id}}')
        self.assertResponseNoErrors(resp, {'outlets': []})

    def test_single_outlet(self):
        outlet = self.create_outlet()
        query_string = "{outlet(id:" + str(outlet.id) + "){id}}"
        resp = self.query(query_string)
        self.assertResponseNoErrors(resp, {"outlet": {"id": str(outlet.id)}})

    def test_create_outlet(self):
        self.make_user_masteradmin()
        business = create_business()
        business_id = business.id
        info = self.create_city()
        city_id = info['city_id']
        type_id = info["outlet_kindid"]
        response = self.query(
            (f'''
            mutation{{
                createOutlet(
                    businessId: \"{business_id}\",
                    kindId: {type_id},
                    name: "green ville",
                    addressLine1: "10/11 Nagera",
                    addressLine2: "Nakawa, Kampala",
                    lga: "Nakawa",
                    cityId: {city_id},
                    phoneNumber: "2567803201607",
                    dateLaunched: "2019-02-27",)
                   {{
                    outlet{{name}}
                }}
            }}
            '''),
        )
        self.assertResponseNoErrors(
            response, {"createOutlet": {
                'outlet': {'name': 'green ville'}
            }})

    def test_update_outlet(self):
        self.make_user_masteradmin()
        outlet = self.create_outlet()
        response = self.query(
            (f'''
            mutation{{
                updateOutlet(
                    id: {outlet.id},
                    name: "green ville",
                    addressLine1: "10/11 Nagera",
                    addressLine2: "Nakawa, Kampala",
                    lga: "Nakawa",
                    phoneNumber: "2567803201607",
                    dateLaunched: "2019-02-27",)
                   {{
                    outlet{{name}}
                }}
            }}
            '''),
        )
        self.assertResponseNoErrors(
            response, {"updateOutlet": {
                'outlet': {'name': 'green ville'}
            }})

    def test_outlet_model(self):
        outlet = self.create_outlet()
        all_outlets = Outlet.objects.all()
        self.assertQuerysetEqual(all_outlets, ['<Outlet: bingo>'])

    def test_country_model(self):
        country = Country.objects.create(name="Kenya")
        all_countries = Country.objects.all()
        self.assertQuerysetEqual(all_countries, ['<Country: Kenya>'])

    def test_city_model(self):
        country = Country.objects.create(name='Kenya')
        city = City.objects.create(name='Nairobi', country_id=country.id)
        all_cities = City.objects.all()
        self.assertQuerysetEqual(all_cities, ['<City: Nairobi>'])

    def test_outletkind_model(self):
        OutletKind.objects.create(name='storefront')
        all_types = OutletKind.objects.all()
        self.assertQuerysetEqual(all_types, ['<OutletKind: storefront>'])

    def test_delete_outlet(self):
        self.make_user_masteradmin()
        outlet = self.create_outlet()
        response = self.query(
            f'mutation{{deleteOutlet(id: {outlet.id}){{success}}}}')
        self.assertIn("success", response["data"]["deleteOutlet"])
