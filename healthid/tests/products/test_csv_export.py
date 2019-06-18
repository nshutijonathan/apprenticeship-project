import base64
from django.urls import reverse
from rest_framework.test import APIClient
from healthid.tests.base_config import BaseConfiguration


class CsvExportTestCase(BaseConfiguration):

    def setUp(self):
        super().setUp()
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            'Basic ' +
            base64.b64encode(b'john.doe@gmail.com:Password123').decode('ascii')
        }
        self.client = APIClient()
        self.url = reverse('export_csv', kwargs={'param': 'products'})

    def test_csv_export_including_specific_fields(self):
        body = {
            "product_name": True,
            "description": True
        }
        response = self.client.post(self.url, body,
                                    format='json', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_csv_export_excluding_specific_fields(self):
        body = {
            "product_name": False,
            "description": False
        }
        response = self.client.post(self.url, body,
                                    format='json', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_csv_export_with_wrong_field_names(self):
        body = {
            "product": False,
            "description": False
        }
        response = self.client.post(self.url, body,
                                    format='json', **self.auth_headers)
        self.assertIn('error', response.data)
        self.assertEqual(response.status_code, 404)

    def test_empty_product_csv_export_succeeds(self):
        self.url = reverse('export_product_csv')
        response = self.client.get(self.url,
                                   format='json', **self.auth_headers)
        content_type = response._headers['content-type'][1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_type, 'text/csv')
