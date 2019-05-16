import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.sales.models import (
    Promotion, PromotionType as PromotionTypeModel
)
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_belongs_to_outlet


class PromotionTypeModelType(DjangoObjectType):
    class Meta:
        model = PromotionTypeModel


class PromotionType(DjangoObjectType):
    class Meta:
        model = Promotion


class Query(graphene.AbstractType):
    outlet_promotions = graphene.List(PromotionType,
                                      outlet_id=graphene.Int(required=True))
    promotion_types = graphene.List(PromotionTypeModelType)

    @login_required
    def resolve_outlet_promotions(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_belongs_to_outlet(user, kwargs.get('outlet_id'))
        return Promotion.objects.filter(outlet=outlet)

    @login_required
    def resolve_promotion_types(self, info, **kwargs):
        return PromotionTypeModel.objects.all()
