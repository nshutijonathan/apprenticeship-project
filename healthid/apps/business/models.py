from django.contrib.auth.models import BaseUserManager
from django.db import models
from healthid.apps.utils.id_generator import id_gen
from healthid.apps.authentication.models import User


class BusinessManager(BaseUserManager):
    """
    Creates a business.
    Validate whethere the busines with same email already exits
    Validate whether business with same legal name exits before
    creating a business

    """

    def create_business(self, **kwargs):
        email = kwargs.get('email')
        trading_name = kwargs.get('trading_name')
        legal_name = kwargs.get('legal_name')
        address = kwargs.get('address')
        phone_number = kwargs.get('phone_number')
        website = kwargs.get('website')
        facebook = kwargs.get('facebook')
        twitter = kwargs.get('twitter')
        instagram = kwargs.get('instagram')
        logo = kwargs.get('logo')
        business = self.model.objects.filter(email=email)
        if business:
            raise ValueError(
                "Business with this email {} already exists".format(email))
        business = self.model.objects.filter(
            legal_name=legal_name)
        if business:
            raise ValueError(
                "Business with this legal name {} already"
                " exists".format(legal_name))
        business = self.model(
            email=email,
            trading_name=trading_name,
            legal_name=legal_name,
            address=address,
            phone_number=phone_number,
            website=website,
            facebook=facebook,
            twitter=twitter,
            instagram=instagram,
            logo=logo
        )
        business.save()
        return business


class Business(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    trading_name = models.CharField(max_length=244)
    legal_name = models.CharField(max_length=244, unique=True)
    address = models.CharField(max_length=244)
    phone_number = models.CharField(max_length=25)
    email = models.EmailField(blank=True, unique=True)
    website = models.CharField(max_length=344)
    facebook = models.CharField(max_length=344)
    twitter = models.CharField(max_length=344)
    instagram = models.CharField(max_length=244)
    logo = models.ImageField(upload_to='logos')
    user = models.ManyToManyField(User)
    objects = BusinessManager()

    def __str__(self):
        return self.legal_name
