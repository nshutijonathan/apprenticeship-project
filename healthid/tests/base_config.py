import json

from django.test import Client, TestCase

from healthid.apps.authentication.models import Role, User
from healthid.apps.outlets.models import City, Country, Outlet, OutletKind
from healthid.apps.products.models import (BatchInfo, MeasurementUnit, Product,
                                           ProductCategory)
from healthid.apps.orders.models import PaymentTerms, Tier, Suppliers
from healthid.apps.sales.models import SalesPrompt
from healthid.apps.preference.models import Timezone, Preference
from healthid.tests.test_fixtures.authentication import login_user_query
from healthid.utils.business_utils.create_business import create_business


class BaseConfiguration(TestCase):
    """
    Base configuration file for all tests.
    """

    @classmethod
    def setUpClass(cls):

        # We need to first run setUpClass function that we
        # inherited from TestCase.
        super(BaseConfiguration, cls).setUpClass()

        # Set up test client for all test classes
        # that will inherit from this class.
        cls.client = Client()

    @classmethod
    def query(cls, query: str = None):
        # Method to run all queries and mutations for tests.
        body = dict()
        body['query'] = query
        response = cls.client.post(
            '/healthid/', json.dumps(body), content_type='application/json')
        json_response = json.loads(response.content.decode())
        return json_response

    @classmethod
    def query_with_token(cls, access_token, query: str = None):
        # Method to run queries and mutations using a logged in user
        # with an authentication token
        body = dict()
        body['query'] = query
        http_auth = 'JWT {}'.format(access_token)
        url = '/healthid/'
        content_type = 'application/json'

        response = cls.client.post(
            url,
            json.dumps(body),
            HTTP_AUTHORIZATION=http_auth,
            content_type=content_type)
        json_response = json.loads(response.content.decode())
        return json_response

    def setUp(self):
        """
        Configurations to be made available before each
        individual test case inheriting from this class.
        """
        self.new_user = {
            "email": "john.doe@gmail.com",
            "mobile_number": "+256 770777777",
            "password": "Password123"
        }
        self.master_admin = {
            "email": "you@example.com",
            "mobile_number": "+256 770777797",
            "password": "Password123"
        }
        self.login_user = {
            "email": "john.doe@gmail.com",
            "password": "Password123"
        }
        self.login_master_admin = {
            "email": "you@example.com",
            "password": "Password123"
        }
        self.update_user_data = {
            'firstname': 'kafuuma',
            'lastname': 'henry',
            'username': 'kafuumahenry',
            'email': 'healthid@gmail.com',
            'phone': +256788088831
        }

        self.user = self.register_user()
        self.business = create_business()
        self.outlet_kind = self.create_outlet_kind()
        self.supplier = self.create_suppliers(self.user)
        self.timezone = Timezone(
            id="285461788", name="Africa/Lagos", time_zone="(GMT+01:00) Lagos")
        self.timezone.save()
        self.outlet = self.create_outlet()
        self.role = self.create_role(role_name="Cashier")
        self.measurement_unit = self.create_measurement_unit()
        self.product_category = self.create_product_category()
        self.product = self.create_product()
        self.batch_info = self.create_batch_info()
        self.sales_prompt = self.create_sales_prompt()

        # register and log in user
        self.outlet.user.add(self.user)
        self.access_token = self.user_login()
        self.master_admin_user = self.register_master_admin()
        self.access_token_master = self.admin_login()
        self.preference = Preference.objects.get()

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")

    def register_user(self):
        """
        register a new user
        """
        email = self.new_user["email"]
        mobile_number = self.new_user["mobile_number"]
        password = self.new_user["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.save()
        return user

    def register_master_admin(self):
        """
        register a master admin
        """
        email = self.master_admin["email"]
        mobile_number = self.master_admin["mobile_number"]
        password = self.master_admin["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.role = Role.objects.create(name='Master Admin')
        self.business.user.add(user)
        user.save()
        return user

    def user_login(self):
        """
        Log in registered user and return a token
        """
        response = self.query(login_user_query.format(**self.login_user))
        return response['data']['tokenAuth']['token']

    def admin_login(self):
        """
        Log in registered user and return a token
        """
        response = self.query(
            login_user_query.format(**self.login_master_admin))
        return response['data']['tokenAuth']['token']

    def create_outlet_kind(self):
        country = Country.objects.create(name='Peru')
        city = City.objects.create(name="Chiclayo", country_id=country.id)
        outlet_kind = OutletKind.objects.create(name="Warehouse")
        info = {"city_id": city.id, "outlet_kindid": outlet_kind.id}
        return info

    def create_outlet(self):
        info = self.outlet_kind
        return Outlet.objects.create(
            name="bingo",
            kind_id=info["outlet_kindid"],
            address_line1="wandegya",
            phone_number="254745345342",
            address_line2="Central, Kla",
            lga="KCCA",
            city_id=info["city_id"],
            date_launched="1995-10-20",
            business_id=self.business.id)

    def create_role(self, role_name):
        return Role.objects.create(name=role_name)

    def create_suppliers(self, user):
        payment_terms = \
            PaymentTerms.objects.create(name="Mobile Banking")
        city = City.objects.get(name="Chiclayo")
        tier = Tier.objects.create(name="exporter")

        return Suppliers.objects.create(
            name='Sport Direct',
            email='sportdirect@mail.com',
            mobile_number='254745345342',
            city=city,
            tier=tier,
            payment_terms=payment_terms,
            user=user)

    def create_measurement_unit(self):
        return MeasurementUnit.objects.create(name='kilogram')

    def create_product_category(self):
        return ProductCategory.objects.create(name='Drinks')

    def create_product(self, product_name='Pizza'):
        return Product.objects.create(
            product_name=product_name,
            sales_price=100,
            product_category=self.product_category,
            measurement_unit=self.measurement_unit,
            prefered_supplier=self.supplier,
            backup_supplier=self.supplier,
            unit_cost=20.3)

    def create_batch_info(self):
        batch_info = BatchInfo.objects.create(
            supplier=self.supplier,
            quantity_received=10,
        )
        batch_info.product.add(self.product)
        batch_info.save()
        return batch_info

    def create_sales_prompt(self):
        return SalesPrompt.objects.create(
            prompt_title="Title for Sales Prompt",
            description="Sales Prompt Description",
            product=self.product,
            outlet=self.outlet
        )
