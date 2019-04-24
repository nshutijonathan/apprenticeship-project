import io

from healthid.utils.orders_utils import add_supplier
from healthid.utils.product_utils.handle_csv_upload import \
    HandleCsvValidations
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
            add_supplier.handle_csv_upload(io_string=io_string)
            message = {"success": "Successfully added supplier(s)"}
            return Response(message, status.HTTP_201_CREATED)
        if param == 'products':
            handle_csv(io_string=io_string)
            message = {"success": "Successfully added products"}
            return Response(message, status.HTTP_201_CREATED)
