import json
from datetime import datetime

from django.forms import model_to_dict
from django.test import Client, TestCase

from healthid.apps.authentication.models import Role, User
from healthid.apps.events.models import Event, EventType
from healthid.apps.orders.models import (Order, PaymentTerms, SupplierNote,
                                         Suppliers, Tier)
from healthid.apps.outlets.models import City, Country, Outlet, OutletKind
from healthid.apps.preference.models import Preference, Timezone
from healthid.apps.products.models import (BatchInfo, MeasurementUnit, Product,
                                           ProductCategory, Quantity)
from healthid.apps.profiles.models import Profile
from healthid.apps.sales.models import SalesPrompt
from healthid.apps.stock.models import StockCountTemplate
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
        self.stock_count_user1 = {
            "email": "arkafuuma@gmail.com",
            "mobile_number": "+256 470777777",
            "password": "Password123"
        }
        self.stock_count_user2 = {
            "email": "arkafuuma2@gmail.com",
            "mobile_number": "+256 570777777",
            "password": "Password123"
        }
        self.master_admin = {
            "email": "you@example.com",
            "mobile_number": "+256 770777797",
            "password": "Password123"
        }

        self.second_master_admin = {
            "email": "you.second@example.com",
            "mobile_number": "+256 770777798",
            "password": "Password1234"
        }

        self.login_second_master_admin = {
            "email": "you.second@example.com",
            "password": "Password1234"
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
        self.outlet = {
            'name': 'bingo',
            'address_line1': "wandegya",
            'phone_number': "254745345342",
            'address_line2': "Central, Kla",
            'lga': "KCCA",
            'date_launched': "1995-10-20"
        }
        self.second_outlet = {
            'name': 'bingow',
            'address_line1': "wandegya ku bitaala",
            'phone_number': "254745345341",
            'address_line2': "Central, Kla",
            'lga': "KCCA",
            'date_launched': "1995-10-20"
        }

        self.user = self.register_user(self.new_user)
        self.business = create_business()
        self.outlet_kind = self.create_outlet_kind()
        self.supplier = self.create_suppliers(self.user)
        self.timezone = Timezone(
            id="285461788", name="Africa/Lagos", time_zone="(GMT+01:00) Lagos")
        self.timezone.save()
        self.outlet = self.create_outlet(self.outlet)
        self.role = self.create_role(role_name="Cashier")
        self.master_admin_role = self.create_role('Master Admin')
        self.measurement_unit = self.create_measurement_unit()
        self.product_category = self.create_product_category()
        self.product = self.create_product()
        self.batch_info = self.create_batch_info()
        self.sales_prompt = self.create_sales_prompt()
        self.suppliers_note = self.create_suppliers_note()
        self.event = self.create_event()
        self.order = self.create_order()

        # register and log in user
        self.outlet.user.add(self.user)
        self.access_token = self.user_login()
        self.master_admin_user = self.register_master_admin(self.master_admin)
        self.second_master_admin_user = self.register_master_admin(
            self.second_master_admin)
        self.second_master_admin_token = self.admin_login(
            self.login_second_master_admin)
        self.access_token_master = self.admin_login(self.login_master_admin)
        self.preference = Preference.objects.filter().first()
        self.second_outlet = self.create_outlet(self.second_outlet)
        self.second_outlet.user.add(self.second_master_admin_user)
        self.outlet.user.add(self.master_admin_user)

        self.create_customer_data = {
            "first_name": "Habib",
            "last_name": "Audu",
            "email": "talktohabib@gmail.com",
            "city_id": self.outlet_kind['city_id'],
            "country_id": self.outlet_kind['country_id'],
            "primary_mobile_number": "+256 788088831",
            "secondary_mobile_number": "+256 788088831",
            "loyalty_member": "true",
            "emergency_contact_email": "talktohabi2@gmail.com"
        }

        self.customer_1 = self.create_customer({
            "first_name": "Dany",
            "last_name": "Stomborn",
            "email": "dany.stomborn@got.com",
            "city_id": self.outlet_kind['city_id'],
            "country_id": self.outlet_kind['country_id'],
            "primary_mobile_number": "+234 788088831",
            "secondary_mobile_number": "+234 788088832",
            "loyalty_member": True,
            "local_government_area": "Heming way",
            "address_line_1": "20, king's Landing",
            "address_line_2": "Esos lane",
            "emergency_contact_name": "Frodo",
            "emergency_contact_email": "saruman@lotr.world",
            "emergency_contact_number": "+234 897090878 "
        })
        self.invoice_data = {
            "outlet_id": self.outlet.id,
            "order_id": self.order.id,
            "image_url": "http://onlineblueprintprinting.com/wp-content/"
            "uploads/free-editable-invoice-template-invoice-template-"
            "free-and-fully-customizable-online-templates.png",
        }

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")

    def register_user(self, user):
        """
        register a new user
        """
        email = user["email"]
        mobile_number = user["mobile_number"]
        password = user["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.save()
        return user

    def register_master_admin(self, master_admin):
        """
        register a master admin
        """
        email = master_admin["email"]
        mobile_number = master_admin["mobile_number"]
        password = master_admin["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.role = self.master_admin_role
        user.save()
        self.business.user.add(user)
        return user

    def user_login(self):
        """
        Log in registered user and return a token
        """
        response = self.query(login_user_query.format(**self.login_user))
        return response['data']['tokenAuth']['token']

    def admin_login(self, admin):
        """
        Log in registered user and return a token
        """
        response = self.query(
            login_user_query.format(**admin))
        return response['data']['tokenAuth']['token']

    def create_outlet_kind(self):
        country = Country.objects.create(name='Peru')
        city = City.objects.create(name="Chiclayo", country_id=country.id)
        outlet_kind = OutletKind.objects.create(name="Warehouse")
        info = {"city_id": city.id, "outlet_kindid": outlet_kind.id,
                "country_id": country.id}
        return info

    def create_outlet(self, outlet):
        info = self.outlet_kind
        return Outlet.objects.create(
            name=outlet["name"],
            kind_id=info["outlet_kindid"],
            address_line1=outlet["address_line1"],
            phone_number=outlet["phone_number"],
            address_line2=outlet["address_line2"],
            lga=outlet['lga'],
            city_id=info["city_id"],
            date_launched=outlet['date_launched'],
            business_id=self.business.id)

    def create_order(self, closed=True):
        """Return an instance of Order.

        If closed is True return a closed order

        Args:
            closed (Bool): order closed flag

        Returns:
            order (:obj) `model`
        """
        return Order.objects.create(
            order_number="5757575",
            name="ututu",
            product_autofill=True,
            supplier_autofill=True,
            delivery_date="2012-12-12",
            sent_status=True,
            destination_outlet_id=self.outlet.id,
            closed=closed
        )

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
        return ProductCategory.objects.create(name='Drinks',
                                              outlet=self.outlet)

    def create_product(self, product_name='Pizza'):
        return Product.objects.create(
            product_name=product_name,
            sales_price=100,
            product_category=self.product_category,
            measurement_unit=self.measurement_unit,
            preferred_supplier=self.supplier,
            backup_supplier=self.supplier,
            unit_cost=20.3, pre_tax_retail_price=25.0)

    def create_batch_info(self):
        batch_info = BatchInfo.objects.create(
            supplier=self.supplier,
            outlet=self.outlet,
            user=self.user
        )
        batch_info.product.add(self.product)
        Quantity.objects.create(
            batch=batch_info, quantity_received=8, is_approved=True,
            product=self.product)
        batch_info.save()
        return batch_info

    def create_sales_prompt(self):
        return SalesPrompt.objects.create(
            prompt_title="Title for Sales Prompt",
            description="Sales Prompt Description",
            product=self.product,
            outlet=self.outlet
        )

    def create_event(
        self, event_title='some event',
        description='urgent event',
    ):
        event_type = EventType.objects.create(name='Outlet Event')
        event = Event.objects.create(
            event_title=event_title, start_date=datetime.now(),
            end_date=datetime.now(), description=description,
            event_type=event_type, start_time=datetime.now(),
            end_time=datetime.now(),
        )
        event.user.add(self.user)
        event.outlet.add(self.outlet)
        return event

    def create_stock_template(self):
        stock_template = StockCountTemplate.objects.create(
            outlet=self.outlet,
            schedule_time=self.event
        )
        stock_template.products.add(self.product)
        stock_template.assigned_users.add(self.user)
        stock_template.designated_users.add(self.user)
        stock_template.save()
        return stock_template

    def create_suppliers_note(self):
        supplier = SupplierNote.objects.create(
            supplier=self.supplier,
            user=self.user,
            note="Amazing supplier"
        )
        supplier.outlet.add(self.outlet)
        return supplier

    @staticmethod
    def create_customer(data):
        return Profile.objects.create(**data)

    @staticmethod
    def customer_fields_to_dict(data):
        customer_data = model_to_dict(data)
        customer_data["city_id"] = customer_data.pop("city")
        customer_data["country_id"] = customer_data.pop("country")
        customer_data["loyalty_member"] = str(
            customer_data["loyalty_member"]).lower()
        return customer_data
