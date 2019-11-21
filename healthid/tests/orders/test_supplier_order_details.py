from healthid.tests.base_config import BaseConfiguration
from healthid.apps.orders.models.orders import Order, OrderDetails
from healthid.utils.orders_utils.supplier_order_details import \
    create_suppliers_order_details
from healthid.tests.test_fixtures.orders import \
    suppliers_order_details, supplier_order_details, modify_order_quantities,\
    remove_order_detail


class TestSupplierOrderDetails(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.order = self.create_order()
        self.order_details = self.create_order_details(self.order)
        self.suppliers_order_details = \
            create_suppliers_order_details(self.order)

    def create_order(self):
        order = Order(name='order',
                      delivery_date='2019-10-05',
                      destination_outlet=self.outlet)
        order.save()
        return order

    def create_order_details(self, order):
        return OrderDetails.objects.create(product=self.product,
                                           ordered_quantity=5,
                                           supplier=self.supplier,
                                           order=order)

    def test_add_product_with_specific_quantity(self):
        response = self.query_with_token(
            self.access_token,
            modify_order_quantities.format(product=self.product.id,
                                           order_id=self.order.id, quantity=5)
        )
        product_quantity = (
            response['data']['addOrderDetails']
            ['suppliersOrderDetails'][0]['orderDetails']
            [0]['orderedQuantity']
        )
        self.assertEquals(product_quantity, 5)

    def test_add_same_product_with_different_quantity(self):
        initial_order = self.query_with_token(
            self.access_token,
            modify_order_quantities.format(
                product=self.product.id,
                order_id=self.order.id,
                quantity=5
            )
        )
        repeat_order = self.query_with_token(
            self.access_token,
            modify_order_quantities.format(
                product=self.product.id,
                order_id=self.order.id,
                quantity=250
            )
        )
        initial_product_quantity = (
            initial_order['data']['addOrderDetails']
            ['suppliersOrderDetails'][0]['orderDetails']
            [0]['orderedQuantity']
        )
        final_product_quantity = (
            repeat_order['data']['addOrderDetails']
            ['suppliersOrderDetails'][0]['orderDetails']
            [0]['orderedQuantity']
        )
        self.assertEquals(initial_product_quantity, 5)
        self.assertEquals(final_product_quantity, 250)

    def test_remove_an_order_detail(self):
        self.query_with_token(
            self.access_token,
            modify_order_quantities.format(
                product=self.product.id,
                order_id=self.order.id,
                quantity=5
            )
        )
        order_detail_id = OrderDetails.objects.get(
            product=self.product.id,
            ordered_quantity=5,
            order_id=self.order.id
        ).id
        self.query_with_token(
            self.access_token,
            remove_order_detail.format(
                order_detail_id=order_detail_id,
            )
        )
        does_exist = OrderDetails.objects.filter(
            product=self.product.id,
            ordered_quantity=5,
            order_id=self.order.id
        ).exists()
        self.assertEquals(does_exist, False)

    def test_create_supplier_order_details_function(self):
        self.assertEqual(len(self.suppliers_order_details), 1)

    def test_user_can_retrieve_suppliers_order_details_for_order(self):
        response = self.query_with_token(
            self.access_token,
            suppliers_order_details.format(order_id=self.order.id)
        )
        self.assertIsNotNone(response['data']['suppliersOrderDetails'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_supplier_order_details_for_order(self):
        response = self.query_with_token(
            self.access_token,
            supplier_order_details.format(
                order_id=self.order.id, supplier_id=self.supplier.id)
        )
        self.assertIsNotNone(response['data']['supplierOrderDetails'])
        self.assertNotIn('errors', response)
