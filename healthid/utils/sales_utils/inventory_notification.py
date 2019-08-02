from healthid.apps.preference.models import OutletPreference
from healthid.apps.sales.sales_velocity import SalesVelocity
from healthid.apps.products.models import Product
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.messages.sales_responses import \
    SALES_ERROR_RESPONSES


def fetch_managers_email(outlet_users):
    for outlet_user in outlet_users:
        if outlet_user.role and outlet_user.role.name == 'Manager':
            return outlet_user.email


def send_manager_email(products, managers_email):
    mail_context = {
        'products': products,
    }
    mail = SendMail(
        to_email=[managers_email],
        subject='Inventory Notification',
        template='email_alerts/reorder_email.html',
        context=mail_context
    )
    mail.send()


def inventory_check(user, products):
    """
    Alert if inventory goes below reorder point.
    Returns:
        None
    """
    outlet = check_user_has_an_active_outlet(user)
    outlet_users = outlet.active_outlet_users
    managers_email = fetch_managers_email(outlet_users)
    products_below_stock = []
    for product in products:
        product_id = product['product_id']
        product_instance = get_model_object(Product, 'id', product_id)
        reorder_point = product_instance.reorder_point
        if reorder_point == 0:
            outlet_preference = get_model_object(OutletPreference,
                                                 'outlet_id',
                                                 outlet.id)
            reorder_point = outlet_preference.reorder_point
        remaining_stock = product_instance.quantity
        sales_velocity = SalesVelocity(
            product_id=product_instance.id,
            outlet_id=product_instance.outlet_id
        ).velocity_calculator()
        (default_sales_velocity, calculated_sales_velocity,
            message) = sales_velocity

        if message is SALES_ERROR_RESPONSES['default_velocity']:
            sales_velocity = default_sales_velocity
        else:
            sales_velocity = calculated_sales_velocity

        time_to_depletion = round(remaining_stock/sales_velocity, 1)
        time_to_reorder = round(time_to_depletion - reorder_point, 1)

        if time_to_reorder < reorder_point:
            products_below_stock.append(product_instance.product_name)

    if products_below_stock:
        send_manager_email(products_below_stock, managers_email)
