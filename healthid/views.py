import csv
import io

from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from healthid.apps.products.models import Product
from healthid.apps.products.serializers import ProductsSerializer
from healthid.utils.orders_utils.add_supplier import add_supplier
from healthid.utils.product_utils.handle_csv_export import handle_csv_export
from healthid.utils.product_utils.handle_csv_upload import HandleCsvValidations
from healthid.utils.constants.product_constants import \
                                                    PRODUCT_INCLUDE_CSV_FIELDS
from healthid.utils.csv_export.generate_csv import generate_csv_response


class HandleCSV(APIView):
    parser_classes = (MultiPartParser, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, param, format=None):
        handle_csv_object = HandleCsvValidations()
        handle_csv = handle_csv_object.handle_csv_upload
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            message = {"error": "Please upload a csv file"}
            return Response(message, status.HTTP_400_BAD_REQUEST)
        data_set = csv_file.read().decode('UTF-8')

        io_string = io.StringIO(data_set)
        next(io_string)

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


class HandleCsvExport(APIView):
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


class EmptyProductCsvExport(APIView):
    """Handle the download of empty CSV file"""

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        """Responds to a get request for csv download.

        Args:
            request(obj): The http request from client.

        Returns:
            The response in a csv format with a status of 200.

        """
        response = generate_csv_response(HttpResponse, 'sample_product.csv',
                                         Product, PRODUCT_INCLUDE_CSV_FIELDS)
        return response
