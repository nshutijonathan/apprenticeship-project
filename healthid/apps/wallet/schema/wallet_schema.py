from graphene_django import DjangoObjectType
from healthid.apps.wallet.models import CustomerCredit


class CustomerCreditType(DjangoObjectType):
    class Meta:
        model = CustomerCredit
