import base64
import os

from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse

from healthid.apps.orders.models import PaymentTerms, Suppliers, Tier
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (supplier_mutation,
                                                    suppliers_query)
from healthid.views import HandleCSV


class SuppliersTestCase(BaseConfiguration):
    def setUp(self):
        super(SuppliersTestCase, self).setUp()
        self.factory = RequestFactory()
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            'Basic ' +
            base64.b64encode(b'john.doe@gmail.com:Password123').decode('ascii')
        }
        call_command('loaddata', 'healthid/fixtures/tests')

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

    def test_create_supplier(self):
        response = self.query_with_token(self.access_token, supplier_mutation)
        self.assertIn('city', response['data']['addSupplier']['supplier'])
        self.assertNotIn("errors", response)

    def test_duplicate_supplier_email(self):
        self.query_with_token(self.access_token, supplier_mutation)
        response = self.query_with_token(self.access_token, supplier_mutation)
        self.assertIn('errors', response)
        self.assertEqual(response['data']['addSupplier'], None)

    def test_suppliers_query(self):
        response = self.query_with_token(self.access_token_master,
                                         suppliers_query)
        self.assertIn('allSuppliers', response['data'])

    def test_csv_file_upload(self):
        path = os.path.join(self.base_path, 'test.csv')
        file = open(path, 'rb')
        request = self.factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='suppliers')
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.data)

    def test_invalid_csv_data(self):
        path = os.path.join(self.base_path, 'invalid_csv.csv')
        file = open(path, 'rb')
        request = self.factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='suppliers')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)

    def test_invalid_csv_format(self):
        path = os.path.join(self.base_path, 'missing_column.csv')
        file = open(path, 'rb')
        request = self.factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
