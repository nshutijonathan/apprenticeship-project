from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.customers import (
    create_customer, customer_query_all, customer_search_query,
    customer_name_query, customer_number_query, customer_id_query)


class TestQueryCustomer(BaseConfiguration):
    """Tests querying customer"""

    def setUp(self):
        super(TestQueryCustomer, self).setUp()
        self.customer = self.query_with_token(
            self.access_token,
            create_customer.format(
                **self.create_customer_data))

    def test_fetch_all_customers(self):
        """
        Tests fetching all customers when one or more has been created
        """
        response = self.query_with_token(
            self.access_token, customer_query_all)
        expected_name = 'Habib'
        self.assertNotIn('errors', response)
        self.assertIn('data', response)
        self.assertEqual(
            expected_name,
            response['data']['customers'][0]['firstName'])

    def test_query_customer_using_name(self):
        name = 'Habib'
        last_name = 'Audu'
        response = self.query_with_token(
            self.access_token,
            customer_name_query.format(name=name))
        self.assertEqual(
            last_name,
            response['data']['customer'][0]['lastName'])

    def test_query_customer_using_mobile_number(self):
        mobile_number = '+256 788088831'
        first_name = 'Habib'
        response = self.query_with_token(
            self.access_token, customer_number_query.format(
                mobile_number=mobile_number))
        self.assertEqual(
            first_name,
            response['data']['customer'][0]['firstName'])

    def test_query_customer_using_id(self):
        customer_id = self.customer['data']['createCustomer']['customer']['id']
        first_name = 'Habib'
        response = self.query_with_token(
            self.access_token, customer_id_query.format(
                customer_id=customer_id))
        self.assertEqual(
            first_name,
            response['data']['customer'][0]['firstName'])

    def test_valid_filter_params(self):
        first_name = 'Habib'
        response = self.query_with_token(
            self.access_token, customer_search_query.format(
                search_key='firstName_Iexact', search_term=first_name))
        self.assertEqual(
            first_name,
            response['data']['filterCustomers']
            ['edges'][0]['node']['firstName'])

    def test_invalid_email_params(self):
        email = 'Habib'
        response = self.query_with_token(
            self.access_token, customer_search_query.format(
                search_key='email_Iexact', search_term=email))
        expected_message = "['Please provide a valid email']"
        self.assertIn('errors', response)
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_invalid_search_params(self):
        first_name = 'H@bib'
        response = self.query_with_token(
            self.access_token, customer_search_query.format(
                search_key='firstName_Iexact', search_term=first_name))
        expected_message = (
            "['Please provide a valid search keyword."
            " Only letters, numbers, and apostrophes allowed']")
        self.assertIn('errors', response)
        self.assertEqual(
            expected_message, response['errors'][0]['message'])
