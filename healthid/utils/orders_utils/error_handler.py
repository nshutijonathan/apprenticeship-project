from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError

from healthid.apps.orders.models import Suppliers


class SuppliersContextManager:
    """
    Manage supppliers model exceptions
    """

    def __init__(self, id):
        self.id = id

    def __enter__(self):
        try:
            supplier = Suppliers.objects.get(id=self.id)
            return supplier
        except ObjectDoesNotExist:
            message = f'supplier with id {self.id} does not exist!'
            raise GraphQLError(message)

    def __exit__(self, exc_type, exc_value, exc_tb):
        return False


class EditSupplierManager:
    """
    Manage exceptions when sending a suppliers edit request
    """

    def __init__(self, email=None):
        self.email = email
        self.supplier = Suppliers()

    def __enter__(self):
        if self.email is not None:
            try:
                supplier = Suppliers.objects.get(email=self.email)
                if supplier:
                    msg = f"Supplier with email {self.email} \
                        already exists!"
                    raise GraphQLError(msg)
            except ObjectDoesNotExist:
                pass
            return self.supplier

    def __exit__(self, exc_type, exc_value, exc_tb):
        return False
