import graphene
import json
from collections import namedtuple, Counter
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.orders.models.orders import (
    SupplierOrderDetails, Order, OrderDetails)
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.orders_utils.inventory_notification import \
    autosuggest_product_order
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet


class SupplierOrderFormOutput(graphene.ObjectType):
    supplier_order_form_id = graphene.String()
    order_id = graphene.Int()
    supplier_id = graphene.String()
    order_name = graphene.String()
    order_number = graphene.String()
    status = graphene.String()
    supplier_order_name = graphene.String()
    supplier_order_number = graphene.String()
    number_of_products = graphene.Int()
    marked_as_sent = graphene.Boolean()


class AutosuggestOrder(graphene.ObjectType):
    product_name = graphene.String()
    suggested_quantity = graphene.String()


class OrderType(DjangoObjectType):
    outlet = graphene.String()

    class Meta:
        model = Order

    def resolve_outlet(self, info):
        return self.name


class OrderDetailsType(DjangoObjectType):
    class Meta:
        model = OrderDetails


class SupplierOrderDetailsType(DjangoObjectType):
    order_details = graphene.List(OrderDetailsType)
    number_of_products = graphene.Int()
    supplier_order_name = graphene.String()
    supplier_order_number = graphene.String()
    deliver_to = graphene.String()
    delivery_due = graphene.Date()
    payment_due = graphene.Date()

    class Meta:
        model = SupplierOrderDetails

    def resolve_number_of_products(self, info):
        return len(self.get_order_details)

    def resolve_order_details(self, info, **kwargs):
        """
        get order details

        Returns:
            list: order details of a particular supplier and order
        """
        return self.get_order_details

    def resolve_supplier_order_name(self, info, **kwargs):
        """
        gets supplier order name

        Returns:
            string: supplier order name from supplier order details
        """
        return self.get_supplier_order_name

    def resolve_supplier_order_number(self, info, **kwargs):
        """
        gets supplier order number

        Returns:
            string: supplier order number from supplier order details
        """
        return self.get_supplier_order_number

    def resolve_deliver_to(self, info, **kwargs):
        """
        gets outlets a supplier is supposed to deliver the order to

        Returns:
            list: outlets supplier is supposed to deliver to from
                  supplier order details
        """
        return self.deliver_to_outlets

    def resolve_delivery_due(self, info, **kwargs):
        """
        gets the date a supplier is supposed to deliver the order

        Returns:
            date: date when the supplier has to deliver order from
                  supplier order details
        """
        return self.delivery_due_date

    def resolve_payment_due(self, info, **kwargs):
        """
        gets when the payment of the supplier should be paid

        Returns:
            date: when the supplier will be paid from the supplier
                  order details
        """
        return self.payment_due_date


class Query(graphene.AbstractType):

    suppliers_order_details = graphene.List(
        SupplierOrderDetailsType, order_id=graphene.Int(required=True))
    supplier_order_details = graphene.Field(
        SupplierOrderDetailsType, supplier_order_form_id=graphene.String(
            required=True)
    )
    orders = graphene.List(OrderType, page_count=graphene.Int(),
                           page_number=graphene.Int())
    order = graphene.Field(OrderType, order_id=graphene.Int(required=True))
    orders_sorted_by_status = graphene.List(OrderType, page_count=graphene.Int(),
                                            page_number=graphene.Int(), status=graphene.String(required=True))
    closed_orders = graphene.List(OrderType, page_count=graphene.Int(),
                                  page_number=graphene.Int())
    total_orders_pages_count = graphene.Int()
    pagination_result = None
    autosuggest_product_order = graphene.List(AutosuggestOrder)

    all_suppliers_order_forms = graphene.List(SupplierOrderFormOutput)

    @login_required
    def resolve_all_suppliers_order_forms(self, info, **kwargs):

        incomplete_orders = []
        complete_orders_with_duplicates = []
        complete_orders_with_no_duplicates = []

        # get all of my orders
        orders = Order.objects.filter(user_id=info.context.user.id)

        # get all of my orders's IDs
        order_ids = [i.__dict__['id'] for i in orders]

        # getting the incomplete order information
        for order_detail_item in orders:
            supplier_order_object = {}
            supplier_order_object['order_name'] = order_detail_item.__dict__[
                'name']
            supplier_order_object['order_id'] = order_detail_item.__dict__[
                'id']
            supplier_order_object['order_number'] = order_detail_item.__dict__[
                'order_number']
            supplier_order_object['status'] = order_detail_item.__dict__[
                'status']
            incomplete_orders.append(supplier_order_object)

        supplier_order_details = SupplierOrderDetails.objects.filter(
            order_id__in=order_ids)

        order_details = OrderDetails.objects.filter(order_id__in=order_ids)

        # get the complete order information
        for sod in supplier_order_details:
            for od in order_details:
                if sod.__dict__['order_id'] == od.__dict__['order_id'] \
                        and sod.__dict__['supplier_id'] == od.__dict__['supplier_id']:

                    supplier_order_object = {}
                    supplier_order_object['supplier_order_form_id'] = sod.__dict__[
                        'id']
                    supplier_order_object['order_id'] = od.__dict__['order_id']
                    supplier_order_object['supplier_id'] = od.__dict__[
                        'supplier_id']
                    supplier_order_object['status'] = "Awaiting order send-out..."
                    supplier_order_object['supplier_order_name'] = od.__dict__[
                        'supplier_order_name']
                    supplier_order_object['supplier_order_number'] = od.__dict__[
                        'supplier_order_number']
                    supplier_order_object['marked_as_sent'] = sod.__dict__[
                        'marked_as_sent']
                    complete_orders_with_duplicates.append(
                        supplier_order_object)

        # converting complete_orders_with_duplicates
        # from a dictionary to an object
        new_list = []
        for res in complete_orders_with_duplicates:
            new_list.append(namedtuple(
                'Struct', res.keys())(*res.values()))

        # counter how many times it repeats itself in order
        # to get the number of products
        new_counter_object = dict(Counter(new_list))
        keys = list(new_counter_object.keys())
        values = list(new_counter_object.values())

        # store supplier order form id as a key and
        # value as a number of products
        key_value_object = {}
        for i, res in enumerate(keys):
            key_value_object[list(keys[i])[0]] = values[i]

        # remove duplicates
        for res in complete_orders_with_duplicates:
            if res not in complete_orders_with_no_duplicates:
                complete_orders_with_no_duplicates.append(res)

        # adding the number of products for each supplier order form
        for res in complete_orders_with_no_duplicates:
            for key, value in key_value_object.items():
                if key == res['supplier_order_form_id']:
                    res['number_of_products'] = value

        union = incomplete_orders + complete_orders_with_no_duplicates
        all_supplier_order_forms = []

        # remove the order which is has a status of ready to be placed because
        # once it has that, it means the real supplier order forms where generated
        # so we use them on it's behalf.
        for res in union:
            if 'waiting for order to be placed' not in res['status'] \
                    and not res.get('marked_as_sent'):
                all_supplier_order_forms.append(namedtuple(
                    'Struct', res.keys())(*res.values()))

        return all_supplier_order_forms

    @login_required
    def resolve_suppliers_order_details(self, info, **kwargs):
        """
        gets order details for suppliers of that order

        Returns:
            list: supplier order details of a particular order
        """
        order = get_model_object(Order, 'id', kwargs.get('order_id'))
        return SupplierOrderDetails.objects.filter(order=order)

    @login_required
    def resolve_supplier_order_details(self, info, **kwargs):
        return SupplierOrderDetails.objects.filter(id=kwargs['supplier_order_form_id']).first()

    @login_required
    def resolve_orders(self, info, **kwargs):
        """
        gets all orders

        Returns:
            list: orders
        """
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        orders_set = Order.objects.filter(
            user_id=info.context.user.id).order_by('id')

        if page_count or page_number:
            orders = pagination_query(
                orders_set, page_count, page_number)
            Query.pagination_result = orders
            return orders[0]
        paginated_response = pagination_query(orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_total_orders_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying, totalOrdersPagesCount query field should
        strictly be called after the orders query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_order(self, info, **kwargs):
        """
        gets a single order

        Returns:
            obj: an order
        """
        return get_model_object(Order, 'id', kwargs.get('order_id'))

    @login_required
    def resolve_orders_sorted_by_status(self, info, **kwargs):
        """
        gets orders that are based on their status

        Returns:
            list: orders
        """
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        status = kwargs.get('status')
        orders_set = SupplierOrderDetails.objects.filter(
            closed=False, status=status).order_by('id')
        if page_count or page_number:
            orders_sorted_by_status = pagination_query(
                orders_set, page_count, page_number)
            Query.pagination_result = orders_sorted_by_status
            return orders_sorted_by_status[0]
        paginated_response = pagination_query(orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_closed_orders(self, info, **kwargs):
        """
        gets orders that have been closed

        Returns:
            list: closed orders
        """
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        closed_orders_set = Order.objects.filter(closed=True).order_by('id')
        if page_count or page_number:
            closed_orders = pagination_query(
                closed_orders_set, page_count, page_number)
            Query.pagination_result = closed_orders
            return closed_orders[0]
        paginated_response = pagination_query(closed_orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_autosuggest_product_order(self, info, **kwargs):
        """
        Auto suggest products that needs to be ordered and the
        quantity that needs to be ordered for based on the sales
        velocity calculator

        Returns:
            list: tuple(product_name, quantity)
        """
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        product_to_order = autosuggest_product_order(outlet=outlet)
        return product_to_order
