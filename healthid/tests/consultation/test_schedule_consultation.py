from django.core.management import call_command

from healthid.apps.authentication.models import User
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.consultation import (create_consultation,
                                                       post_consultation,
                                                       schedule_mutation)


class ScheduleConsultationTestCase(BaseConfiguration):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'healthid/fixtures/consultation_data')
        call_command('loaddata', 'healthid/fixtures/event_types.json')
        self.consultation_type = create_consultation(
            self.outlet.id, "consultation")

    def test_empty_db(self):
        resp = self.query_with_token(
            self.access_token_master,
            '{scheduledConsultations {id}}')
        self.assertResponseNoErrors(resp, {'scheduledConsultations': []})

    def test_single_consultation(self):
        schedule = post_consultation(self.consultation_type)
        resp = self.query_with_token(
            self.access_token_master,
            f'query{{scheduledConsultation(id: \"{schedule.id}\"){{id}}}}'
        )
        self.assertResponseNoErrors(
            resp, {'scheduledConsultation': {'id': schedule.id}})

    def test_schedule_consultation(self):
        user = User.objects.get(email="you@example.com")
        start_date = "2019-04-06"
        resp = self.query_with_token(
            self.access_token_master,
            schedule_mutation(self.consultation_type.id, user.id, start_date)
        )
        self.assertResponseNoErrors(
            resp, {
                'schedule': {
                    'scheduleConsultation': {
                        'customerName': 'Nangai',
                        'event': {
                            'startDate': start_date
                            },
                        'consultants': [
                            {
                                'id': user.id
                            }
                        ]
                        }
                    }
                })
