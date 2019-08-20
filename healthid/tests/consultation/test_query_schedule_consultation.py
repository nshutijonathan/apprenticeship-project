from faker import Faker
from healthid.tests.base_config import BaseConfiguration

from healthid.tests.test_fixtures.consultations import (
    retrieve_schedule_consultations)
from healthid.tests.factories import (
    ConsultationItemFactory, CustomerConsultationFactory)

fake = Faker()


class TestQueryScheduleConsultation(BaseConfiguration):
    def setUp(self):
        super(TestQueryScheduleConsultation, self).setUp()
        self.consultation_type = ConsultationItemFactory(
            consultation_name=fake.word(),
            description=fake.text(max_nb_chars=50),
            consultant_role="Pharmacist",
            approved_delivery_formats=["Telephonic"],
            outlet_id=self.outlet.id,
            minutes_per_session=fake.random_int(min=1, max=60),
            price_per_session=fake.random_int()
        )
        self.booking_item = CustomerConsultationFactory(
            consultation_type=self.consultation_type,
            consultant=fake.name(),
            status="Now"
        )

    def test_user_can_retrieve_bookings(self):
        response = self.query_with_token(
            self.access_token_master, retrieve_schedule_consultations)
        self.assertEqual(
            response['data']['bookings'][0]['id'],
            str(self.booking_item.id))
