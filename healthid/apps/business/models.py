from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q
from graphql import GraphQLError

from healthid.apps.authentication.models import User
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.app_utils.validators import validate_email
from healthid.utils.business_utils.validators import ValidateBusiness


class BusinessManager(BaseUserManager):
    """
    Creates a business.
    Validate whethere the busines with same email already exits
    Validate whether business with same legal name exits before
    creating a business

    """

    def create_business(self, **kwargs):
        '''Method to save a business in the database
        '''
        business = Business.objects.filter(
            Q(business_email=kwargs['business_email']) |
            Q(legal_name=kwargs['legal_name']))
        if business:
            raise GraphQLError('Business already exists!')
        business_email = validate_email(kwargs['business_email'])
        ValidateBusiness().validate_business(**kwargs)
        business = self.model(
            business_email=business_email,
            trading_name=kwargs.get('trading_name'),
            legal_name=kwargs.get('legal_name'),
            address_line_1=kwargs.get('address_line_1'),
            address_line_2=kwargs.get('address_line_2'),
            city=kwargs.get('city'),
            country=kwargs.get('country'),
            local_government_area=kwargs.get('local_government_area'),
            phone_number=kwargs.get('phone_number'),
            website=kwargs.get('website'),
            facebook=kwargs.get('facebook'),
            twitter=kwargs.get('twitter'),
            instagram=kwargs.get('instagram'),
            logo=kwargs.get('logo')
        )
        business.save()
        return business


class Business(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    trading_name = models.CharField(max_length=244)
    legal_name = models.CharField(max_length=244, unique=True)
    address_line_1 = models.CharField(max_length=244, blank=True)
    address_line_2 = models.CharField(max_length=244, blank=True)
    local_government_area = models.CharField(max_length=244, blank=True)
    country = models.CharField(max_length=244, blank=True)
    city = models.CharField(max_length=244, blank=True)
    phone_number = models.CharField(max_length=25)
    business_email = models.EmailField(blank=True, unique=True)
    website = models.CharField(max_length=344)
    facebook = models.CharField(max_length=344)
    twitter = models.CharField(max_length=344)
    instagram = models.CharField(max_length=244)
    logo = models.URLField()
    user = models.ManyToManyField(User)
    objects = BusinessManager()

    def __str__(self):
        return self.legal_name
