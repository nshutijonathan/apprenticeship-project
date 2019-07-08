from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import create_measuremt_unit
from healthid.utils.messages.common_responses import\
     SUCCESS_RESPONSES, ERROR_RESPONSES


class TestMeasurementUnit(BaseConfiguration):
    """
    class handles all tests for meaurement units
    """

    def test_create_measurement_unit(self):
        """
        test meaurement creation
        """
        reponse = self.query_with_token(self.access_token_master,
                                        create_measuremt_unit)
        self.assertIn(SUCCESS_RESPONSES[
                      "creation_success"].format("Measurement Unit"),
                      reponse['data']['createMeasurementUnit']['message'])
        self.assertIn('data', reponse)
        self.assertNotIn('errors', reponse)

    def test_duplicate_unit(self):
        """
        test duplicate  meauremnt unit
        """
        self.query_with_token(self.access_token_master, create_measuremt_unit)
        duplicate_measurement = self.query_with_token(self.access_token_master,
                                                      create_measuremt_unit)
        self.assertIn(ERROR_RESPONSES[
                      "duplication_error"].format(
                                        "MeasurementUnit with name tablets"),
                      duplicate_measurement['errors'][0]['message'])
        self.assertIn('errors', duplicate_measurement)
