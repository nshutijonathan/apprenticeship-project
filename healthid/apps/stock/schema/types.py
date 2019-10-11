from graphene_django import DjangoObjectType
from healthid.apps.stock.models import (
    StockTransfer, StockCountTemplate, StockCount)


class StockTransferType(DjangoObjectType):
    class Meta:
        model = StockTransfer


class StockCountTemplateType(DjangoObjectType):
    class Meta:
        model = StockCountTemplate


class StockCountType(DjangoObjectType):
    class Meta:
        model = StockCount
