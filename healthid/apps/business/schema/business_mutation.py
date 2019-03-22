import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.authentication.utils.decorator import master_admin_required
from healthid.apps.business.models import Business


class BusinesType(DjangoObjectType):
    class Meta:
        model = Business


class CreateBusiness(graphene.Mutation):
    """Creates business
    Checks whether the person creating business is super user
    if not stops person from creating business
    returns user who created the business
    """
    business = graphene.Field(BusinesType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        trading_name = graphene.String()
        legal_name = graphene.String()
        address = graphene.String()
        phone_number = graphene.String()
        email = graphene.String()
        website = graphene.String()
        facebook = graphene.String()
        twitter = graphene.String()
        instagram = graphene.String()
        logo = graphene.String()
        user = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        business = Business.objects.create_business(
            trading_name=kwargs.get('trading_name'),
            legal_name=kwargs.get('legal_name'),
            address=kwargs.get('address'),
            phone_number=kwargs.get('phone_number'),
            email=kwargs.get('email'),
            website=kwargs.get('website'),
            facebook=kwargs.get('facebook'),
            twitter=kwargs.get('twitter'),
            instagram=kwargs.get('instagram'),
            logo=kwargs.get('logo')
        )
        business.user.add(user)
        business.save()
        success = ["Business successfully created"]
        return CreateBusiness(business=business, success=success)


class UpdateBusiness(graphene.Mutation):
    """
    Updates a Business by Master Admin |super user
    Arguments: trading name, legal name, number, address
    """
    business = graphene.Field(BusinesType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String()
        trading_name = graphene.String()
        legal_name = graphene.String()
        address = graphene.String()
        phone_number = graphene.String()
        email = graphene.String()
        website = graphene.String()
        facebook = graphene.String()
        twitter = graphene.String()
        instagram = graphene.String()
        logo = graphene.String()
        user = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        business = Business.objects.get(pk=id)
        for(key, value) in kwargs.items():
            if key is not None:
                setattr(business, key, value)
        business.save()
        success = ["Business has been updated successfully"]

        return UpdateBusiness(
            business=business,
            success=success
        )


class DeleteBusiness(graphene.Mutation):
    """Deletes a Business
    This also perform the delete action after validating user
    """
    business = graphene.Field(BusinesType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, id):
        business = Business.objects.get(pk=id)
        business.delete()
        success = ["Business has been deleted successfully"]

        return DeleteBusiness(
            success=success
        )


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    delete_business = DeleteBusiness.Field()
    update_business = UpdateBusiness.Field()
