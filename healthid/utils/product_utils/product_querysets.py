from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError

from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import Product, BatchInfo


class ProductModelQuery:
    """
    This method help to query all models relating to product
  """

    def query_product_id(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            raise GraphQLError(f"Product with id "
                               f"{product_id} does not exist.")

    def query_batch_info(self, batch_id):
        try:
            return BatchInfo.objects.get(id=batch_id)
        except ObjectDoesNotExist:
            raise GraphQLError(f"Batch Info with id "
                               f"{batch_id} does not exist.")

    def query_supplier_id(self, supplier_id):
        try:
            return Suppliers.objects.get(supplier_id=supplier_id)
        except ObjectDoesNotExist:
            raise GraphQLError(f"Supplier with id "
                               f"{supplier_id} does not exist.")
