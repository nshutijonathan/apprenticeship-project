import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.business.models import Business
from healthid.apps.authentication.schema.auth_queries \
    import UserType
from healthid.apps.authentication.querysets.user_query \
    import UserModelQuery
from healthid.utils.business_utils.business_query \
    import BusinessModelQuery
from healthid.utils.auth_utils.decorator import master_admin_required
from graphql import GraphQLError


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
        trading_name = graphene.String(required=True)
        legal_name = graphene.String(required=True)
        address_line_1 = graphene.String(required=True)
        address_line_2 = graphene.String()
        phone_number = graphene.String(required=True)
        business_email = graphene.String(required=True)
        city = graphene.String(required=True)
        country = graphene.String(required=True)
        local_government_area = graphene.String()
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
            address_line_1=kwargs.get('address_line_1'),
            address_line_2=kwargs.get('address_line_2'),
            phone_number=kwargs.get('phone_number'),
            business_email=kwargs.get('business_email'),
            city=kwargs.get('city'),
            country=kwargs.get('country'),
            local_government_area=kwargs.get('local_government_area'),
            website=kwargs.get('website'),
            facebook=kwargs.get('facebook'),
            twitter=kwargs.get('twitter'),
            instagram=kwargs.get('instagram'),
            logo=kwargs.get('logo')
        )
        business.user.add(user)
        business.save()
        success = ["Business successfully created!"]
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
        address_line_1 = graphene.String()
        address_line_2 = graphene.String()
        phone_number = graphene.String()
        business_email = graphene.String()
        city = graphene.String()
        country = graphene.String()
        local_government_area = graphene.String()
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
        id = kwargs.get('id')
        business = Business.objects.get(pk=id)

        business_users = business.user.all()

        if user not in business_users:
            raise GraphQLError("You can't update a business you're \
not assigned to!")
        for(key, value) in kwargs.items():
            if key is not None:
                setattr(business, key, value)
        business.save()
        success = ["Business has been updated successfully"]

        return UpdateBusiness(
            business=business,
            success=success
        )


class AddUserBusiness(graphene.Mutation):
    class Arguments:
        user_id = graphene.String(required=True)
        business_id = graphene.String(required=True)

    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @master_admin_required
    def mutate(root, info, **kwargs):
        user_id = kwargs.get('user_id')
        business_id = kwargs.get('business_id')
        user_instance = UserModelQuery().query_user_id(user_id)
        business_instance = BusinessModelQuery().query_business_id(business_id)
        business_instance.user.add(user_instance)
        user_instance.save()
        message = [
            f"Successfully added User with {user_instance.email}"
            f" to {business_instance.legal_name} business"
        ]
        return AddUserBusiness(
            user=user_instance,
            message=message)


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
    add_user_business = AddUserBusiness.Field()
