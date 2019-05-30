import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.sales.schema.cart_query import CartItemType
from healthid.apps.sales.models import Cart, CartItem
from healthid.apps.products.models import Product


class AddCartItem(graphene.Mutation):
    '''
    Adds a product along with quantity to cart.

    args:
        product_id: id of product you want to add to cart.
        quantity: amount of the product to add to cart.

    returns:
        success: message to signal that a product has been added to cart
        cart_item: the product that has been added to cart alon with the
                   quantity
    '''
    class Arguments:
        product_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)

    success = graphene.String()
    cart_item = graphene.Field(CartItemType)

    @login_required
    def mutate(self, info, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=info.context.user)
        product_id = kwargs.get('product_id')
        product = get_model_object(Product, 'id', product_id)
        if not product.is_approved:
            raise GraphQLError(f'{product.product_name} isn\'t approved yet.')
        quantity = kwargs.get('quantity')
        if quantity > product.quantity:
            raise GraphQLError(
                f'There is only quantity {product.quantity} of '
                f'{product.product_name} available in stock.'
            )
        cart_item = CartItem(product=product, quantity=quantity)
        with SaveContextManager(cart_item) as cart_item:
            cart.items.add(cart_item)
            return AddCartItem(success='Product added to cart.',
                               cart_item=cart_item)


class Mutation(graphene.ObjectType):
    add_to_cart = AddCartItem.Field()
