import io

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from healthid.utils.orders_utils import add_supplier


class HandleCSV(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, param, format=None):
        csv_file = request.FILES['file']
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)
        if param == 'suppliers':
            add_supplier.handle_csv_upload(io_string=io_string)
            message = {
                "success": "Successfully added supplier(s)"
            }
            return Response(message, status.HTTP_201_CREATED)
