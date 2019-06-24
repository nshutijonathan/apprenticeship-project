import os
from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase
from healthid.tests.authentication.test_data import loginUser_mutation
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import supplier_mutation
from healthid.views import HandleCSV


class TestCsvUpload(BaseConfiguration, JSONWebTokenTestCase):
    def setUp(self):
        super(TestCsvUpload, self).setUp()
        # Log in user and use fetched token for endpoint authorization
        email = self.new_user["email"]
        password = self.new_user["password"]
        response = self.client.execute(loginUser_mutation.format(
            email=email,
            password=password)
        )
        token = response.data['loginUser']['restToken']

        self.query_with_token(self.access_token,
                              supplier_mutation)
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            ' Token ' + str(token)
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
        self.assertIn('noOfProductsAdded', response.data)
