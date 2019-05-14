from django.db.models import Q

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.query_objects import GetObjectList


class StockCounts:

    @staticmethod
    def get_template_fields(**kwargs):
        products = None
        if kwargs.get('product_ids'):
            products = GetObjectList.get_objects(
                Product, kwargs.get('product_ids'))
        assigned_users = None
        if kwargs.get('assigned_user_ids'):
            assigned_users = GetObjectList.get_objects(
                User, kwargs.get('assigned_user_ids'))
        designated_users = None
        if kwargs.get('designated_user_ids'):
            admin_user_ids = [user.id for user in User.objects.filter(
                Q(role__name='Operations Admin') | Q(role__name='Master Admin')
                | Q(role__name='Store Manager'))]
            user_ids = admin_user_ids+kwargs.get('assigned_user_ids')
            designated_users = GetObjectList.get_objects(
                User, user_ids)
        schedule_time = None
        if kwargs.get('event_id'):
            schedule_time = get_model_object(
                Event, 'id', kwargs.get('event_id'))
        outlet = None
        if kwargs.get('outlet_id'):
            outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))

        return{
            'products': products,
            'assigned_users': assigned_users,
            'designated_users': designated_users,
            'schedule_time': schedule_time,
            'outlet': outlet
        }

    @staticmethod
    def add_fields_to_template(template_instance, **kwargs):
        for (key, value) in kwargs.items():
            if key in ('outlet', 'schedule_time') and value is not None:
                setattr(template_instance, key, value)
        products = kwargs.get('products')
        if products:
            template_instance.products.clear()
            for product in products:
                template_instance.products.add(product)
        assigned_users = kwargs.get('assigned_users')
        if assigned_users:
            template_instance.assigned_users.clear()
            for user in assigned_users:
                template_instance.assigned_users.add(user)
        designated_users = kwargs.get('designated_users')
        if designated_users:
            template_instance.designated_users.clear()
            for user in designated_users:
                template_instance.designated_users.add(user)
        return template_instance


stock_counts = StockCounts()
