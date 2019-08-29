import factory

from datetime import datetime, timedelta
from faker import Faker

from django.conf import settings

from healthid.apps.orders.models import (Order, SupplierOrderDetails,
                                         OrderDetails, Suppliers,
                                         PaymentTerms, Tier, SupplierNote)
from healthid.apps.products.models import (ProductCategory, Product,
                                           MeasurementUnit,
                                           BatchInfo, Quantity)
from healthid.apps.authentication.models import Role
from healthid.apps.consultation.models import (
    ConsultationCatalogue, CustomerConsultation, MedicalHistory)
from healthid.apps.business.models import Business
from healthid.apps.outlets.models import (Country, City, OutletKind, Outlet)
from healthid.apps.preference.models import Timezone
from healthid.apps.profiles.models import Profile
from healthid.apps.sales.models import Sale, PromotionType, Promotion


fake = Faker()


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    email = factory.Sequence(lambda x: "user%d@email.com" % x)
    mobile_number = factory.Sequence(lambda x: "25470000004%d" % x)
    is_active = True
    is_superuser = False
    first_name = factory.Sequence(lambda x: "Bob%d" % x)
    last_name = "Watshisface"
    username = factory.Sequence(lambda x: "user_%d" % x)
    secondary_email = factory.Sequence(lambda x: "user%dother@email.com" % x)
    secondary_phone_number = "254722000000"
    profile_image = "http://image.com"
    job_title = "Worker"


class roleFactory(factory.DjangoModelFactory):

    class Meta:
        model = Role

    name = "User"


class TimezoneFactory(factory.DjangoModelFactory):

    class Meta:
        model = Timezone

    id = "285461788"
    name = "Africa/Nairobi"
    time_zone = "African/Nairobi"


class TierFactory(factory.DjangoModelFactory):

    class Meta:
        model = Tier

    name = factory.Sequence(lambda x: f"Tier %d" % x)


class PaymentTermsFactory(factory.DjangoModelFactory):

    class Meta:
        model = PaymentTerms

    name = factory.Sequence(lambda x: f"Payment Term %d" % x)


class CountryFactory(factory.DjangoModelFactory):

    class Meta:
        model = Country

    name = factory.Sequence(lambda x: "Country %d" % x)


class CityFactory(factory.DjangoModelFactory):

    class Meta:
        model = City

    name = factory.Sequence(lambda x: "City %d" % x)
    country = factory.SubFactory(CountryFactory)


class BusinessFactory(factory.DjangoModelFactory):

    class Meta:
        model = Business

    trading_name = factory.Sequence(lambda x: "Business %d" % x)
    legal_name = factory.Sequence(lambda x: "Legal Business %d" % x)
    address_line_1 = "House 1"
    address_line_2 = "Some Street"
    local_government_area = "No idea"
    country = "BestCountryEver"
    city = "BestCityEver"
    phone_number = "254700000000"
    business_email = factory.Sequence(lambda x: "business%d@email.com" % x)
    website = factory.Sequence(lambda x: "www.business%d.com" % x)
    facebook = "unknown"
    twitter = "unknown"
    instagram = "unknown"
    logo = factory.Sequence(
        lambda x: "http://www.business%d_logo.com" % x)

    @factory.post_generation
    def user(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for u in extracted:
                self.user.add(u)


class OutletKindFactory(factory.DjangoModelFactory):

    class Meta:
        model = OutletKind

    name = factory.Sequence(lambda x: "Outlet Kind %d" % x)


class OutletFactory(factory.DjangoModelFactory):

    class Meta:
        model = Outlet

    kind = factory.SubFactory(OutletKindFactory)
    name = factory.Sequence(lambda x: "Outlet %d" % x)
    address_line1 = "Building 1"
    address_line2 = "Some Street"
    lga = "NO idea"
    city = factory.SubFactory(CityFactory)
    phone_number = "254700000000"
    date_launched = datetime.today()
    prefix_id = "Blah"
    business = factory.SubFactory(BusinessFactory)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)


class SuppliersFactory(factory.DjangoModelFactory):

    class Meta:
        model = Suppliers

    name = factory.Sequence(lambda x: "Supplier %d" % x)
    email = factory.Sequence(lambda x: "supplier%d@supplier%d.com" % (x, x))
    mobile_number = "254700000000"
    address_line_1 = "Building 1"
    address_line_2 = "This & That Street"
    lga = "NO idea"
    city = factory.SubFactory(CityFactory)
    tier = factory.SubFactory(TierFactory)
    logo = "http://unkownurl.something"
    commentary = "no comment"
    payment_terms = factory.SubFactory(PaymentTermsFactory)
    user = factory.SubFactory(UserFactory)
    is_approved = False


class MeasurementUnitFactory(factory.DjangoModelFactory):

    class Meta:
        model = MeasurementUnit

    name = factory.Sequence(lambda x: "Unit %d" % x)


class ProductCategoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = ProductCategory

    name = factory.Sequence(lambda x: "Category %d" % x)


class ProductFactory(factory.DjangoModelFactory):

    class Meta:
        model = Product

    product_category = factory.SubFactory(ProductCategoryFactory)
    product_name = factory.Sequence(lambda x: "Product %d" % x)
    measurement_unit = factory.SubFactory(MeasurementUnitFactory)
    sku_number = factory.Sequence(lambda x: "000%d" % x)
    description = "blah blah blah"
    brand = "Brand1"
    manufacturer = "Manufacturer1"
    sales_price = 100.00
    preferred_supplier = factory.SubFactory(SuppliersFactory)
    backup_supplier = factory.SubFactory(SuppliersFactory)
    outlet = factory.SubFactory(OutletFactory)
    user = factory.SubFactory(UserFactory)
    admin_comment = ""
    markup = 25
    auto_price = True
    loyalty_weight = 0
    image = "http://example.com"
    is_active = True
    reorder_point = 2
    reorder_max = 0
    request_declined = False
    is_approved = True


class OrderFactory(factory.DjangoModelFactory):

    class Meta:
        model = Order

    order_number = factory.Sequence(lambda x: "order_%d" % x)
    name = factory.Sequence(lambda x: "Order %d" % x)
    destination_outlet = factory.SubFactory(OutletFactory)
    delivery_date = datetime.now()
    closed = False


class OrderDetailsFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderDetails

    product = factory.SubFactory(ProductFactory)
    quantity = 3
    supplier = factory.SubFactory(SuppliersFactory)
    price = 1000.00
    order = factory.SubFactory(OrderFactory)


class SupplierOrderDetailsFactory(factory.DjangoModelFactory):

    class Meta:
        model = SupplierOrderDetails

    additional_notes = "blah blah blah"
    order = factory.SubFactory(OrderFactory)
    supplier = factory.SubFactory(SuppliersFactory)


class CustomerFactory(factory.DjangoModelFactory):

    class Meta:
        model = Profile

    email = factory.Sequence(lambda x: "customer%d@user%d.com" % (x, x))
    first_name = fake.first_name()
    last_name = fake.last_name()
    primary_mobile_number = factory.Sequence(lambda x: "+234600000%d" % x)
    city = factory.SubFactory(CityFactory)
    country = factory.SubFactory(CountryFactory)


class ConsultationItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = ConsultationCatalogue

    consultation_name = fake.name()
    description = fake.text()
    outlet = factory.SubFactory(OutletFactory)
    minutes_per_session = fake.random_int(min=1, max=60)
    approved_delivery_formats = ["Telephonic"]
    price_per_session = fake.random_int()


class CustomerConsultationFactory(factory.DjangoModelFactory):

    class Meta:
        model = CustomerConsultation

    customer = factory.SubFactory(CustomerFactory)
    consultation_type = factory.SubFactory(ConsultationItemFactory)
    consultant = fake.name()
    booked_by = factory.SubFactory(UserFactory)
    status = "Now"


class MedicalHistoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = MedicalHistory

    consultation = factory.SubFactory(CustomerConsultationFactory)
    medical_notes = fake.text()
    author = fake.name()
    authorized_by = factory.SubFactory(UserFactory)


class SaleFactory(factory.DjangoModelFactory):

    class Meta:
        model = Sale

    sales_person = factory.SubFactory(UserFactory)
    customer = factory.SubFactory(CustomerFactory)
    outlet = factory.SubFactory(OutletFactory)
    amount_to_pay = fake.random_int()
    discount_total = fake.random_int()
    sub_total = fake.random_int()
    paid_amount = fake.random_int()
    change_due = fake.random_int()
    payment_method = "cash"
    notes = fake.text()
    loyalty_earned = fake.random_int(min=0, max=1)


class PromotionTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = PromotionType

    name = factory.Sequence(lambda x: "Promotion Type %d" % x)


class PromotionFactory(factory.DjangoModelFactory):

    class Meta:
        model = Promotion

    promotion_type = factory.SubFactory(PromotionTypeFactory)
    outlet = factory.SubFactory(OutletFactory)
    title = factory.Sequence(lambda x: "Promotion Title %d" % x)
    description = fake.text()
    discount = fake.random_int(min=1, max=100000000)
    is_approved = True

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for product in extracted:
                self.products.add(product)


class BatchInfoFactory(factory.DjangoModelFactory):

    class Meta:
        model = BatchInfo

    batch_no = factory.Sequence(lambda x: "Batch no 0%d" % x)
    supplier = factory.SubFactory(SuppliersFactory)
    date_received = datetime.now()
    expiry_date = datetime.now() + timedelta(days=100)
    unit_cost = fake.random_int()
    sold_out = False
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    service_quality = fake.random_int(min=2, max=3)
    delivery_promptness = True
    comment = factory.Sequence(lambda x: "Batch comment %d" % x)


class QuantityFactory(factory.DjangoModelFactory):

    class Meta:
        model = Quantity

    batch = factory.SubFactory(BatchInfoFactory)
    is_approved = True
    quantity_received = fake.random_int(min=100, max=1000)
    quantity_remaining = fake.random_int(min=100, max=1000)


class SupplierNote(factory.DjangoModelFactory):
    class Meta:
        model = SupplierNote

    supplier = factory.SubFactory(SuppliersFactory)
    user = factory.SubFactory(UserFactory)
    note = fake.text()

    @factory.post_generation
    def outlet(self, create, extracted, **kwargs):
        """
        Method for establishing a many to many relationship
        """
        if not create:
            return

        if extracted:
            # A list of outlet instances were passed in and should be used,
            # for the many to many relationship.
            for outlt in extracted:
                self.outlet.add(outlt)
