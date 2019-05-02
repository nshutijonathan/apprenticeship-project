from rest_framework.exceptions import NotFound


class HandleCsvExport():

    @staticmethod
    def capitalize(word):
        return ' '.join(word.split('_')).upper()

    @classmethod
    def write_csv(cls, product, request):
        if request.data is not None:
            for key, value in request.data.items():
                if value is False:
                    del product[key]
        product = {
            cls.capitalize(key): value for key,
            value in product.items()}
        return product

    @staticmethod
    def validate_request_data(custom_headers, headers, key, value):
        if key not in headers and isinstance(value, bool):
            message = {"error": f"{key} is not a valid field!"}
            raise NotFound(message)
        if not value:
            headers.remove(key)
        if value is True:
            custom_headers.append(key)


handle_csv_export = HandleCsvExport()
