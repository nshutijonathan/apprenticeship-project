import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.wallet.schema.wallet_schema import CustomerCreditType
from healthid.apps.profiles.models import Profile
from healthid.apps.wallet.models import CustomerCredit
from healthid.apps.preference.models import Currency
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.preference_utils.outlet_preference import (
    get_user_outlet_currency_id)
from healthid.utils.messages.customer_responses import CUSTOMER_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.preferences_responses import (
    PREFERENCE_ERROR_RESPONSES)


class CreateCustomerCredit(graphene.Mutation):
    """
    Creates a customer credit account

    Args:
        customer_id (int): id for customer to create credit account

    returns:
         success message and details of credit account created if successful,
         otherwise a GraphQLError is raised
    """
    customer_credit = graphene.Field(CustomerCreditType)
    message = graphene.String()

    class Arguments:
        customer_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        customer_id = kwargs.get("customer_id")
        customer = get_model_object(
            Profile, "id", customer_id)

        if CustomerCredit.objects.filter(customer_id=customer_id).exists():
            raise GraphQLError(
                CUSTOMER_ERROR_RESPONSES[
                    "customer_credit_double_creation_error"
                ])

        user = info.context.user
        outlet_currency_id = get_user_outlet_currency_id(user)

        currency = get_model_object(
            Currency, "id", outlet_currency_id,
            message=PREFERENCE_ERROR_RESPONSES["invalid_currency"].format(
                outlet_currency_id))

        customer_credit = CustomerCredit(
            customer=customer, credit_currency=currency)
        with SaveContextManager(customer_credit, model=CustomerCredit):
            pass
        return CreateCustomerCredit(
            message=SUCCESS_RESPONSES[
                "creation_success"].format("Customer's credit account"),
            customer_credit=customer_credit)


class Mutation(graphene.ObjectType):
    create_customer_credit = CreateCustomerCredit.Field()
