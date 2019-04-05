from healthid.tests.base_config import BaseConfiguration
from healthid.apps.business.tests.utils import create_business
from healthid.apps.outlets.models import City, Country, Outlet, OutletKind


class OutletBaseTest(BaseConfiguration):

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

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")
