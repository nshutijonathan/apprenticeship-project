from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.business import (authentic_business,
                                                   update_business,
                                                   delete_business,
                                                   missing_business_email,
                                                   missing_trading_name,
                                                   missing_address_line_1,
                                                   missing_city,
                                                   missing_phone_number
                                                   )


class GraphQLTestCase(BaseConfiguration):

    def test_create_business(self):
        """Test that a business can be created
        """
        response = self.query_with_token(
            self.access_token_master, authentic_business)
        self.assertIn('data', response)

    def test_create_business_without_email(self):
        """Test that a business can't be created without a business
        email
        """
        response = self.query_with_token(
            self.access_token_master, missing_business_email)
        self.assertEqual(response['errors'][0]['message'],
                         'Please input a valid email')

    def test_create_business_without_trading_name(self):
        """Test that a business can't be created without a trading
        name
        """
        response = self.query_with_token(
            self.access_token_master, missing_trading_name)
        self.assertEqual(response['errors'][0]['message'],
                         'Both trading name and legal name are required!')

    def test_create_business_without_address_line_1(self):
        """Test that a business can't be created without a address line 1
        """
        response = self.query_with_token(
            self.access_token_master, missing_address_line_1)
        self.assertEqual(response['errors'][0]['message'],
                         'Address Line 1 is required!')

    def test_create_business_without_city(self):
        """Test that a business can't be created without a city
        """
        response = self.query_with_token(
            self.access_token_master, missing_city)
        self.assertEqual(response['errors'][0]['message'],
                         'Both city and country are required!')

    def test_create_business_without_phone_number(self):
        """Test that a business can't be created without a city
        """
        response = self.query_with_token(
            self.access_token_master, missing_phone_number)
        self.assertEqual(response['errors'][0]['message'],
                         'Phone number is required!')

    def test_update_business(self):
        """Test that a business can be updated
        """
        business = self.query_with_token(
            self.access_token_master, authentic_business)
        response = self.query_with_token(self.access_token_master,
                                         update_business(
                                             business[
                                                 'data']
                                             ['createBusiness']
                                             ['business']['id']))
        self.assertIn('data', response)

    def test_delete_business(self):
        """Test that a business can be deleted
        """
        business = self.query_with_token(
            self.access_token_master, authentic_business)
        response = self.query_with_token(self.access_token_master,
                                         delete_business(
                                             business['data']
                                             ['createBusiness']
                                             ['business']['id']))
        self.assertIn('data', response)
