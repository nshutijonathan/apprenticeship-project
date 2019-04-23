import os
import base64
from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import supplier_mutation
from healthid.views import HandleCSV


class TestCsvUpload(BaseConfiguration):
    def setUp(self):
        super(TestCsvUpload, self).setUp()
        self.query_with_token(self.access_token,
                              supplier_mutation)
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            'Basic ' +
            base64.b64encode(b'john.doe@gmail.com:Password123').decode('ascii')
        }
        call_command('loaddata', 'healthid/fixtures/product_csv')

    def test_csv_file_upload(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'product.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['products']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='products')
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.data)
