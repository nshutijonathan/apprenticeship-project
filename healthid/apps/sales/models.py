from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.db.models.signals import pre_save

from healthid.apps.authentication.models import User
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product, BatchInfo
from healthid.apps.profiles.models import Profile

from healthid.models import BaseModel
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.sales_utils.initiate_sale import initiate_sale
from healthid.utils.sales_utils.validate_sale import SalesValidator
from healthid.utils.sales_utils.validators import check_approved_sales


class PromotionType(BaseModel):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    name = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.name


class Promotion(BaseModel):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    title = models.CharField(max_length=140, unique=True)
    promotion_type = models.ForeignKey(PromotionType, on_delete=models.CASCADE)
    description = models.TextField()
    products = models.ManyToManyField(Product, blank=True)
    discount = models.DecimalField(decimal_places=2, max_digits=10)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class SalesPrompt(BaseModel):
    prompt_title = models.CharField(max_length=244, unique=True)
    description = models.CharField(
        max_length=244, default="Sales prompt descripttion:")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.prompt_title


class Cart(models.Model):
    '''
    defines cart model.
    args:
        user: owner of the cart.
        items: products along with the quantity and their total that
               have been added to the cart
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem')

    @property
    def total(self):
        '''
        method that calculates the total price of all the items in cart
        '''
        return self.items.all().aggregate(Sum('item_total'))['item_total__sum']


class CartItem(models.Model):
    '''
    defines cart item model
    args:
        product: product to be added to cart
        quantity: amount of product to be added to cart
        item_total: price of the product based on the quantity
    '''
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    item_total = models.DecimalField(default=0.00,
                                     max_digits=10,
                                     decimal_places=2)

    def __str__(self):
        return str(self.id)


def update_item_total(**kwargs):
    """
    function that calculates the price of product being added to cart
    based on the quantity being added, this is triggered before a cart
    item is saved
    """
    cart_item = kwargs.get('instance')
    cart_item.item_total = \
        cart_item.product.get_sales_price * cart_item.quantity


pre_save.connect(update_item_total, sender=CartItem)


class Sale(BaseModel):
    """
    Defines sale model
    Attributes:
            sales_person: Holds employee who made the transaction
            outlet: Holds outlet referencing id.
            customer: Holds a customer who bought the drugs if provided..
            sub_total: Holds the total minus discount.
            amount_to_pay = Holds the total amount including discounts.
            paid_cash  = Holds the paid cash amount
            change_due = Holds the remaining balance
            payment_method: Holds payment method e.g. cash/cash
            notes: Holds note about the sale
    """

    sales_person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sold_by')
    customer = models.ForeignKey(
        Profile,  on_delete=models.CASCADE, null=True)

    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    amount_to_pay = models.DecimalField(max_digits=12, decimal_places=2)
    discount_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    change_due = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=35, default="cash")
    notes = models.TextField(blank=True, null=True)
    loyalty_earned = models.PositiveIntegerField(default=0)

    def _validate_sales_details(self, **kwargs):
        """
        This method handles all validations related to sale fields
        Arguments:
            kwargs: information about sale
        """
        sold_products = kwargs.get('products')
        sales_validator = SalesValidator(sold_products)
        sales_validator.check_sales_fields_validity(**kwargs)
        sales_validator.check_validity_of_ids()
        sales_validator.check_product_discount()
        sales_validator.check_product_price()
        sales_validator.check_payment_method(**kwargs)
        sold_product_instances = sales_validator.check_validity_quantity_sold()
        return sold_product_instances

    @property
    def get_default_register(self):
        """
        Returns a default register for each outlet
        """
        try:
            register = self.outlet.outlet_register.all().first()
            return register.id
        except ObjectDoesNotExist:
            return None

    def create_sale(self, info, **kwargs):
        """
        This method create a sale after it has been validated
        by _validate_sales_details()
        Arguments:
            kwargs: information about sale
            info: information about the logged in user
        """
        sales_person = info.context.user

        customer_id = kwargs.get('customer_id')
        outlet_id = kwargs.get('outlet_id')
        sold_products = kwargs.get('products')
        discount_total = kwargs.get('discount_total')
        sub_total = kwargs.get('sub_total')
        amount_to_pay = kwargs.get('amount_to_pay')
        paid_amount = kwargs.get('paid_amount')
        payment_method = kwargs.get('payment_method')
        change_due = kwargs.get('change_due')
        notes = kwargs.get('notes')

        outlet = get_model_object(Outlet, "id", outlet_id)

        sold_product_instances = Sale._validate_sales_details(self, **kwargs)

        sale = Sale(sales_person=sales_person,
                    outlet=outlet,
                    payment_method=payment_method,
                    discount_total=discount_total,
                    sub_total=sub_total,
                    amount_to_pay=amount_to_pay,
                    paid_amount=paid_amount,
                    change_due=change_due,
                    notes=notes)

        with SaveContextManager(sale) as sale:
            loyalty_points_earned = initiate_sale(
                sold_product_instances,
                sold_products,
                sale,
                SaleDetail,
                BatchHistory)
            if customer_id:
                customer = get_model_object(Profile, "id", customer_id)
                sale.customer = customer
                if customer.loyalty_member:
                    sale.loyalty_earned = loyalty_points_earned
                    customer.loyalty_points += loyalty_points_earned
                    customer.save()
                sale.save()
        return sale

    def sales_history(self, outlet_id=None, search=None):
        sales = Sale.objects.filter(outlet_id=outlet_id)

        if search:
            search_keys = (
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__email__icontains=search) |
                Q(saledetail__product__product_name__icontains=search) |
                Q(notes__icontains=search)
            )
            sales = sales.filter(search_keys)
        return sales

    class Meta:
        ordering = ['-created_at']


class SaleDetail(BaseModel):
    """
    Defines sale detail model
    Attributes:
        product: Holds a reference to products to be sold
        sale:  Holds a sale reference to this product
        quantity:  Holds the quantity to be sold of a product
        price: Holds the price for each product
        note: Holds note about the product
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    discount = models.FloatField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, null=True)


class SaleReturn(BaseModel):
    """
    Defines sale return model
    Attributes:
        cashier(obj): Holds employee id who made the return initiation
        customer(obj): Holds customer who earlier bought if provided
        sale(obj): Holds id of sale reference to this product
        outlet(int): Holds the outlet id
        return_note(str): Holds note for return reason
        return_amount(float): Holds the amount to return the customer
        refund_compensation_type(str): Either cash or store credit.
    """
    cashier = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='cashier', null=True)
    customer = models.ForeignKey(
        Profile,  on_delete=models.SET_NULL, null=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.SET_NULL, null=True)
    return_note = models.CharField(max_length=80, blank=True)
    return_amount = models.DecimalField(max_digits=12, decimal_places=2)
    refund_compensation_type = models.CharField(max_length=80)

    def create_return(self, user, **kwargs):
        """This function initiates a return of products sold
        Args:
            user: the logged in user
            sale_id(int): id referencing that sale we are returning from
            outlet_id(int): outlet we are returning to to
            sale_id(int): id referencing that sale we are returning from
            return_amount(int): pay back amount to user for goods returned
            return_note(str): Holds return reason about the product
            returned_products(objs): Holds products being returned
            refund_compensation_type(str): Either cash or store credit


        Returns:
            salereturn(obj): which is saved in the table sale.salereturn

        """
        cashier = user
        sales_instance = get_model_object(
            Sale, 'id', kwargs.get('sale_id'))
        customer = sales_instance.customer
        outlet_instance = get_model_object(
            Outlet, 'id', kwargs.get('outlet_id'))
        return_validator = SalesValidator(kwargs.get('returned_products'))
        return_validator.check_product_returnable()
        return_validator.check_product_dates_for_return(
            outlet_instance, sales_instance)

        sales_return = SaleReturn(
            cashier=cashier, customer=customer, sale=sales_instance)
        for (key, value) in kwargs.items():
            setattr(sales_return, key, value)
        with SaveContextManager(sales_return, model=SaleReturn)as sales_return:
            pass
        sale_return_detail_list = []
        for product in kwargs.get('returned_products'):
            product_instance = get_model_object(
                Product, 'id', product.product_id)
            sales_return_detail = SaleReturnDetail(
                product=product_instance,
                sales_return=sales_return,
                quantity=product.quantity,
                price=product.price,
                resellable=product.resellable,
                return_reason=product.return_reason
            )
            sale_return_detail_list.append(sales_return_detail)
        SaleReturnDetail.objects.bulk_create(sale_return_detail_list)
        return sales_return

    def approve_sales_return(self, user, receipt,  **kwargs):
        returned_sales = kwargs.get('returned_sales')
        sales_id = kwargs.get('sales_id')
        sales_return_id = kwargs.get('sales_return_id')

        sales_return = get_model_object(SaleReturn, 'id', sales_return_id)

        check_approved_sales(returned_sales, SaleReturnDetail)

        for returned_sale in returned_sales:
            returned_sale_detail = get_model_object(
                SaleReturnDetail, 'id', returned_sale)

            batch_histories = BatchHistory.objects.filter(
                sale_id=sales_id,
                product_id=returned_sale_detail.product_id)

            returned_quantity = returned_sale_detail.quantity

            self.return_batch_quantity(batch_histories, receipt,
                                       returned_quantity, returned_sale_detail,
                                       sales_return_id, user)
        return sales_return

    def return_batch_quantity(self, batch_histories, receipt,
                              returned_quantity, returned_sale_detail,
                              sales_return_id, user):
        for batch_history in batch_histories:
            batch = get_model_object(BatchInfo, 'id',
                                     batch_history.batch_info.id)
            batch_quantity = batch.quantity

            quantity = batch.batch_quantities.filter(
                is_approved=True).first()

            if returned_sale_detail.resellable:
                if returned_quantity > batch_history.quantity_taken:
                    quantity.quantity_remaining = \
                        batch_quantity + batch_history.quantity_taken
                    quantity.save()
                    returned_quantity -= batch_history.quantity_taken
                else:
                    quantity.quantity_remaining = \
                        batch_quantity + returned_quantity
                    quantity.save()
            returned_sale_detail.is_approved = True
            returned_sale_detail.done_by = user
            returned_sale_detail.save()
        receipt.sales_return_id = sales_return_id
        receipt.save()


class SaleReturnDetail(BaseModel):
    """
    Defines return detail model
    Attributes:
        product(obj): Holds a reference to products to be returned
        sales_return(obj): Holds a sale return reference to this product
        quantity(int):  Holds the quantity to be sold of a product
        price(float): Holds the price for each product
        return_reason(str): Holds enum return reason about the product
        is_approved(bool): Holds boolean for particular product return approved
    """
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    sales_return = models.ForeignKey(
        SaleReturn, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    return_reason = models.CharField(max_length=80)
    is_approved = models.BooleanField(default=False)
    resellable = models.BooleanField(default=False)

    def __str__(self):
        return self.return_reason


class BatchHistory(BaseModel):
    batch_info = models.ForeignKey(
        BatchInfo, on_delete=models.SET_NULL, null=True,
        related_name='batch_info_history')
    sale = models.ForeignKey(
        Sale, on_delete=models.SET_NULL, null=True,
        related_name='sale_batch_history')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True,
        related_name='quantity_by_batches')
    quantity_taken = models.PositiveIntegerField()
