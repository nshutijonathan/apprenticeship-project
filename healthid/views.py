import csv
import io
from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from healthid.apps.products.models import Product, BatchInfo
from healthid.apps.profiles.models import Profile
from healthid.apps.products.serializers import ProductsSerializer
from healthid.utils.orders_utils.add_supplier import add_supplier
from healthid.utils.product_utils.handle_csv_export import handle_csv_export
from healthid.utils.product_utils.handle_csv_upload import HandleCsvValidations
from healthid.utils.constants.product_constants import (
    PRODUCT_INCLUDE_CSV_FIELDS, BATCH_INFO_CSV_FIELDS)
from healthid.utils.constants.customer_constants import (
    CUSTOMERS_INCLUDE_CSV_FIELDS)
from healthid.utils.csv_export.generate_csv import generate_csv_response
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from rest_framework.exceptions import APIException
from healthid.utils.customer_utils.handle_customer_csv_upload import\
    HandleCustomerCSVValidation
from healthid.utils.messages.customer_responses import SUCCESS_RESPONSES


class HandleCSV(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    parser_classes = (MultiPartParser, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, param, format=None):
        """
        Rest API post method that is meant to handle the mass,
        upload of information from csv files
        :param request: Will be used to extract the file type
        :param param: endpoint parameter confirming the nature of info,
                      expected in the csv
        :param format:
        :return: Throws error on validation failure and returns,
                  success on Successful data upload
        """
        handle_csv_object = HandleCsvValidations()
        handle_customer_csv_object = HandleCustomerCSVValidation()
        handle_csv = handle_csv_object.handle_csv_upload
        handle_customer_csv_upload =\
            handle_customer_csv_object.handle_customer_csv_upload
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            message = {"error": "Please upload a csv file"}
            return Response(message, status.HTTP_400_BAD_REQUEST)
        data_set = csv_file.read().decode('UTF-8')

        io_string = io.StringIO(data_set)
        next(io_string)
        try:
            if param == 'suppliers':

                user = request.user
                add_supplier.handle_csv_upload(user, io_string)
                message = {
                    "success": "Successfully added supplier(s)"
                }
                return Response(message, status.HTTP_201_CREATED)
            if param == 'products':

                quantity_added = handle_csv(io_string=io_string)
                message = {
                    "success": "Successfully added products",
                    "noOfProductsAdded": quantity_added,
                }
                return Response(message, status.HTTP_201_CREATED)
            if param == 'customers':
                customers_added = handle_customer_csv_upload(io_string)
                message = {
                    "success": SUCCESS_RESPONSES["csv_upload_success"],
                    "noOfCustomersAdded": customers_added,
                }
                return Response(message, status.HTTP_201_CREATED)
        except Exception as e:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({
                "errors": str(e)
            })


class HandleCsvExport(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )
    serializer_class = ProductsSerializer

    def post(self, request, param):
        if param == 'products':
            limit = request.data.get('limit', None)
            query_set = Product.objects.filter(is_approved=True)[:limit]
            serializer = self.serializer_class(query_set, many=True)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = \
                'attachment; filename="products.csv"'
            headers = self.serializer_class.Meta.fields.copy()
            if request.data is not None:
                custom_headers = list()
                for key, value in request.data.items():
                    handle_csv_export.validate_request_data(
                        custom_headers, headers, key, value)
            headers = custom_headers if custom_headers else headers
            headers = \
                [handle_csv_export.capitalize(word) for word in headers]
            writer = csv.DictWriter(
                response,
                fieldnames=headers,
                extrasaction='ignore')
            writer.writeheader()
            for product in serializer.data:
                product = handle_csv_export.write_csv(product, request)
                writer.writerow(product)
            return response


class EmptyCsvFileExport(APIView):
    """Handle the download of empty CSV file"""
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )

    def get(self, request, param):
        """Responds to a get request for csv download based on params

        Args:
            request(obj): The http request from client.

        Returns:
            The response in a csv format with a status of 200.

        """
        if param == 'products':
            response = generate_csv_response(
                HttpResponse,
                'sample_product.csv',
                Product,
                PRODUCT_INCLUDE_CSV_FIELDS)
        elif param == 'customers':
            response = generate_csv_response(
                HttpResponse,
                'sample_customers.csv',
                Profile,
                CUSTOMERS_INCLUDE_CSV_FIELDS)
        elif param == 'batch_info':
            response = generate_csv_response(HttpResponse,
                                             'sample_batch_info.csv',
                                             BatchInfo,
                                             BATCH_INFO_CSV_FIELDS,
                                             name='batch')
        else:
            return Response(ERROR_RESPONSES["wrong_param"],
                            status=status.HTTP_404_NOT_FOUND)
        return response
