from django.core.management import call_command

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures import consultation
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.consultation_reponses import \
     CONSULTATION_ERROR_RESPONSES


class TestAddConsultation(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.consultationName = "Dental surgery"
        call_command('loaddata', 'healthid/fixtures/consultation_data')

    def test_create_consultation(self):
        """method for creating a cosultation"""
        response = self.query_with_token(
            self.access_token_master,
            consultation.add_consultation(self.outlet.id,
                                          self.consultationName))

        self.assertIn(SUCCESS_RESPONSES[
                       "creation_success"].format("Consultation type"),
                      "".join(response['data'][
                                       "createConsultation"]["success"]))

    def test_create_duplicate_consultation(self):
        """method for creating a duplicate cosultation"""
        self.query_with_token(
            self.access_token_master,
            consultation.add_consultation(self.outlet.id,
                                          self.consultationName))
        response = self.query_with_token(
            self.access_token_master,
            consultation.add_consultation(self.outlet.id,
                                          self.consultationName))
        self.assertIn(
            CONSULTATION_ERROR_RESPONSES[
                    "duplicate_consultation_error"].format("Dental surgery"),
            response['errors'][0]["message"])

    def test_create_consultation_with_wrong_outlet_id(self):
        """method for creating a consultation with an \
            outlet id that doenot exist """
        outletId = 30
        response = self.query_with_token(
            self.access_token_master,
            consultation.add_consultation(outletId, self.consultationName))
        self.assertIn(CONSULTATION_ERROR_RESPONSES[
                       "inexistent_outlet"].format("30"),
                      response['errors'][0]["message"])

    def test_query_a_single_consultation(self):
        consultation1 = self.query_with_token(
            self.access_token_master,
            consultation.add_consultation(self.outlet.id,
                                          self.consultationName))
        id = consultation1['data']['createConsultation']['consultation']['id']

        response = self.query_with_token(
            self.access_token, consultation.consultations.format(**{'id': id}))
        self.assertIsNotNone(response['data']['consultation'])
