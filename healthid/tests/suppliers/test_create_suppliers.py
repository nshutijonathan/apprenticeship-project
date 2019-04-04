import os

from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse

from healthid.apps.orders.models import PaymentTerms, Suppliers, Tier
from healthid.views import HandleCSV

from healthid.tests.test_fixtures.suppliers import (supplier_mutation,
                                                    suppliers_query)
from healthid.tests.base_config import BaseConfiguration


class SuppliersTestCase(BaseConfiguration):
    def setUp(self):
        super(SuppliersTestCase, self).setUp()
        call_command('loaddata', 'tests')

    def test_models(self):
        supplier = Suppliers()
        supplier.name = "Ntale"
        tier = Tier()
        tier.name = 'manufacturer'
        payment_term = PaymentTerms()
        payment_term.name = 'on credit'
        assert(str(supplier) == 'Ntale')
        assert(str(tier) == 'manufacturer')
        assert(str(payment_term) == 'on credit')

    def test_suppliers_query(self):
        response = self.query_with_token(self.access_token, suppliers_query)
        self.assertIn('data', response)

    def test_create_supplier(self):
        response = self.query_with_token(self.access_token, supplier_mutation)
        self.assertIn('data', response)

    def test_duplicate_supplier_email(self):
        self.query_with_token(self.access_token, supplier_mutation)
        response = self.query_with_token(self.access_token, supplier_mutation)
        self.assertIn('errors', response)

    def test_csv_file_upload(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'test.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse(
                'handle_csv', args=['suppliers']), {
                'file': file})
        view = HandleCSV.as_view()
        response = view(request, param='suppliers')
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.data)

    def test_invalid_csv_data(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'invalid_csv.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse(
                'handle_csv', args=['suppliers']), {
                'file': file})
        view = HandleCSV.as_view()
        response = view(request, param='suppliers')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
