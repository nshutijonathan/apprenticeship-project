import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import User
from healthid.apps.authentication.schema.auth_queries import UserType
from healthid.apps.business.models import Business
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.business_utils.validators import ValidateBusiness


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
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        ValidateBusiness().validate_business(**kwargs)
        business = Business()
        for key, value in kwargs.items():
            setattr(business, key, value)

        with SaveContextManager(business, model=Business) as business:
            business.user.add(user)
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
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        business = get_model_object(Business, 'id', id)
        business_users = business.user.all()

        if user not in business_users:
            raise GraphQLError("You can't update a business you're \
not assigned to!")
        for(key, value) in kwargs.items():
            if key is not None:
                setattr(business, key, value)
        msg = 'Business with legal name or email provided already exists.'
        with SaveContextManager(business, message=msg):
            success = ["Business has been updated successfully"]
            return UpdateBusiness(business=business, success=success)


class AddUserBusiness(graphene.Mutation):
    class Arguments:
        user_id = graphene.String(required=True)
        business_id = graphene.String(required=True)

    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, **kwargs):
        user_id = kwargs.get('user_id')
        business_id = kwargs.get('business_id')
        user_instance = get_model_object(User, 'id', user_id)
        business_instance = get_model_object(Business, 'id', business_id)
        business_instance.user.add(user_instance)
        user_instance.save()
        message = [
            f"Successfully added User with {user_instance.email}"
            f" to {business_instance.legal_name} business"
        ]
        return AddUserBusiness(user=user_instance, message=message)


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
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        business = get_model_object(Business, 'id', id)
        business.delete(user)
        success = ["Business has been deleted successfully"]

        return DeleteBusiness(success=success)


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    delete_business = DeleteBusiness.Field()
    update_business = UpdateBusiness.Field()
    add_user_business = AddUserBusiness.Field()
