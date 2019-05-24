from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.products.models import Product
from graphql.error import GraphQLError
from healthid.apps.orders.models.orders import OrderDetails
from healthid.utils.app_utils.database import get_model_object


class AddOrderDetails:
    @staticmethod
    def check_list_length(list1, list2, **kwargs):
        name1 = kwargs.get('name1')
        name2 = kwargs.get('name2')
        if len(list1) != len(list2):
            msg = f'{name1} list is not equal to {name2} list!'
            raise GraphQLError(msg)

    @classmethod
    def check_product_exists(self, product_list):
        products = []
        for product_id in product_list:
            product = get_model_object(Product, 'id', product_id)
            products.append(product.id)
        return products

    @classmethod
    def add_supplier(cls, kwargs, supplier):
        products_list = kwargs.get('products')
        products = cls.check_product_exists(products_list)
        for product_id in products:
            supplier_id = next(supplier)
            order_detail = \
                get_model_object(OrderDetails, 'product_id', product_id)
            get_model_object(Suppliers, 'id', supplier_id)
            order_detail.supplier_id = supplier_id
            order_detail.save()
        return order_detail

    @classmethod
    def supplier_autofill(cls, kwargs):
        products_list = kwargs.get('products')
        products = cls.check_product_exists(products_list)
        for product_id in products:
            order_detail = \
                get_model_object(OrderDetails, 'product_id', product_id)
            product = get_model_object(Product, 'id', product_id)
            order_detail.supplier = product.prefered_supplier
            order_detail.save()
        return order_detail

    @classmethod
    def add_product_quantity(cls, kwargs, order, quantity):
        products_list = kwargs.get('products')
        products = cls.check_product_exists(products_list)
        object_list = list()  # list to hold order details instances
        for product_id in products:
            product = \
                get_model_object(Product, 'id', product_id)
            order_details = OrderDetails()
            order_details.order = order
            order_details.product = product
            order_details.quantity = next(quantity)
            object_list.append(order_details)
        OrderDetails.objects.bulk_create(object_list)
        return order_details

    @classmethod
    def product_quantity_autofill(cls, kwargs, order):
        products_list = kwargs.get('products')
        products = cls.check_product_exists(products_list)
        object_list = list()  # list to hold order details instances
        for product_id in products:
            product = \
                get_model_object(Product, 'id', product_id)
            order_details = OrderDetails()
            order_details.order = order
            order_details.product = product
            order_details.quantity = product.autofill_quantity
            object_list.append(order_details)
        OrderDetails.objects.bulk_create(object_list)
        return order_details


add_order_details = AddOrderDetails()
