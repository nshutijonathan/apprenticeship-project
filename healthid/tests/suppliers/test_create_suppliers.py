import os
from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase
from healthid.apps.orders.models import PaymentTerms, Suppliers, Tier
from healthid.tests.authentication.test_data import loginUser_mutation
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (supplier_mutation,
                                                    suppliers_query,
                                                    supplier_query_by_id,
                                                    supplier_query_by_name)
from healthid.views import HandleCSV
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from rest_framework.test import APIClient
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.tests.factories import SuppliersFactory


class SuppliersTestCase(BaseConfiguration, JSONWebTokenTestCase):
    def setUp(self):
        super(SuppliersTestCase, self).setUp()
        self.factory = RequestFactory()
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        # Log in user and use fetched token for endpoint authorization
        email = self.new_user["email"]
        password = self.new_user["password"]
        login_response = self.client.execute(loginUser_mutation.format(
            email=email,
            password=password)
        )
        token = login_response.data['loginUser']['restToken']

        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            ' Token ' + str(token)
        }
        call_command('loaddata', 'healthid/fixtures/tests')
        self.view = HandleCSV.as_view()
        self.client = APIClient()
        self.url = reverse('export_csv', kwargs={'param': 'products'})

        self.supplier_1 = SuppliersFactory()

        self.supplier_data = {
            "id": self.supplier_1.id,
            "name": self.supplier_1.name
        }

    def handle_csv_request(self, path):
        file = open(path, 'rb')
        request = self.factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.auth_headers)
        self.view
        return request

    def test_models(self):
        supplier = Suppliers()
        supplier.name = "Ntale"
        tier = Tier()
        tier.name = 'manufacturer'
        payment_term = PaymentTerms()
        payment_term.name = 'on credit'
        assert (str(supplier) == 'Ntale')
        assert (str(tier) == 'manufacturer')
        assert (str(payment_term) == 'on credit')

    def test_duplicate_supplier_email(self):
        self.query_with_token(self.access_token, supplier_mutation)
        response = self.query_with_token(self.access_token, supplier_mutation)
        self.assertIn('errors', response)
        self.assertIn(ERROR_RESPONSES[
                      "duplication_error"].format(
            "Suppliers with email email@ntale.com"),
            response['errors'][0]['message'])

    def test_suppliers_query(self):
        response = self.query_with_token(self.access_token_master,
                                         suppliers_query)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_supplier_query_by_id(self):
        response = self.query_with_token(self.access_token_master,
                                         supplier_query_by_id.format(
                                             **self.supplier_data))
        supplier_id = self.supplier_data['id']

        self.assertNotIn('errors', response)
        self.assertEqual(supplier_id, response['data']['singleSupplier']['id'])

    def test_supplier_query_by_name(self):
        response = self.query_with_token(self.access_token_master,
                                         supplier_query_by_name.format(
                                             **self.supplier_data))
        supplier_name = self.supplier_data['name']

        self.assertNotIn('errors', response)
        self.assertEqual(
            supplier_name, response['data']['singleSupplier']['name'])

    def test_supplier_query_with_empty_field(self):
        data = {
            "name": ""
        }
        response = self.query_with_token(self.access_token_master,
                                         supplier_query_by_name.format(
                                             **data))
        message = ORDERS_ERROR_RESPONSES[
            "invalid_supplier_field"]
        self.assertEqual(
            message,
            response['errors'][0]['message'])

    def test_create_supplier(self):
        response = self.query_with_token(self.access_token, supplier_mutation)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_csv_file_upload(self):
        path = os.path.join(self.base_path, 'test.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.data)

    def test_invalid_csv_data(self):
        path = os.path.join(self.base_path, 'invalid_csv.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', str(response.data))

    def test_invalid_csv_format(self):
        path = os.path.join(self.base_path, 'missing_column.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', str(response.data))

    def test_empty_suppliers_csv_export_succeeds(self):
        self.url = reverse('export_csv_file', kwargs={'param': 'suppliers'})
        response = self.client.get(self.url,
                                   format='json', **self.auth_headers)
        content_type = response._headers['content-type'][1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_type, 'text/csv')

    def test_empty_suppliers_csv_export_failure(self):
        self.url = reverse('export_csv_file', kwargs={'param': 'supplier'})
        response = self.client.get(self.url,
                                   format='json', **self.auth_headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, ERROR_RESPONSES['wrong_param'])
