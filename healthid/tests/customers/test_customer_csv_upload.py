import os
from django.test import RequestFactory
from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase
from healthid.tests.authentication.test_data import loginUser_mutation
from healthid.tests.base_config import BaseConfiguration
from healthid.views import HandleCSV
from healthid.tests.factories import CountryFactory, CityFactory
from healthid.utils.messages.customer_responses import SUCCESS_RESPONSES


class TestCustomerCsvUpload(BaseConfiguration, JSONWebTokenTestCase):
    def setUp(self):
        super(TestCustomerCsvUpload, self).setUp()
        # Log in user and use fetched token for endpoint authorization
        email = self.new_user["email"]
        password = self.new_user["password"]
        response = self.client.execute(loginUser_mutation.format(
            email=email,
            password=password)
        )
        token = response.data['loginUser']['restToken']
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
                ' Token ' + str(token)
        }
        CountryFactory(name="Nigeria")
        CityFactory(name="Lagos")

    def test_customers_csv_file_upload(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'customers.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['customers']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='customers')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["success"],
                         SUCCESS_RESPONSES["csv_upload_success"])
        self.assertEqual(response.data["noOfCustomersAdded"], 4)
