from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.business.models import Business
from healthid.models import BaseModel
from healthid.utils.outlet_utils.validators import \
    check_user_can_be_activated_deactivated


class Country(BaseModel):
    name = models.CharField(max_length=244, unique=True)

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(max_length=244)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("name", "country"))

    def __str__(self):
        return self.name


class OutletKind(BaseModel):
    name = models.CharField(max_length=244)

    def __str__(self):
        return self.name


class Outlet(BaseModel):
    id = models.AutoField(primary_key=True)
    kind = models.ForeignKey(OutletKind, on_delete=models.CASCADE)
    name = models.CharField(max_length=244)
    address_line1 = models.CharField(max_length=244)
    address_line2 = models.CharField(max_length=244)
    lga = models.CharField(max_length=244)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=25)
    date_launched = models.DateField()
    prefix_id = models.CharField(max_length=9, null=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    users = models.ManyToManyField(
        User, related_name='outlets', through='OutletUser')

    class Meta:
        unique_together = (("name", "business"))

    def __str__(self):
        return self.name

    def activate_deactivate_user(self, logged_in_user, **kwargs):
        """
        Method to activate or deactivate user in an outlet

        Args:
            logged_in_user(obj): Currently logged in user

        Returns:
            outlet_user(obj): user who has been activated or deactivated
            message(string): message to signal if a user has been
                             activated or deactivated
        """
        message, outlet_user = check_user_can_be_activated_deactivated(
            self, OutletUser, logged_in_user, **kwargs)
        outlet_user.is_active_outlet = kwargs.get('is_active')
        outlet_user.save()
        return outlet_user, message

    @property
    def outlet_users(self):
        """
        Method that gets all users of the outlet

        Returns:
            list(obj): users that belong to the outlet
        """
        return self.users.all()

    @property
    def active_outlet_users(self):
        """
        Method that gets all the active users of the outlet

        Returns:
            list(obj): users that active in the outlet
        """
        outlet_users = self.outletuser_set.filter(is_active_outlet=True)
        return [outlet_user.user for outlet_user in outlet_users]

    @property
    def get_manager(self):
        """
        Method that get the manager of the outlet

        Returns:
            list(obj): user manager active in the outlet
        """
        outlet_user = self.outletuser_set.filter(
                       is_active_outlet=True).filter(
                       user__role__name='Manager').first()
        return outlet_user.user


class OutletUser(models.Model):
    """
    Model for outlet users

    Attributes:
        user(obj): user of an outlet
        outlet(obj): outlet the user belongs to
        is_active_outlet(boolean): True if the user is active in the
                                   outlet else False
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    is_active_outlet = models.BooleanField(default=False)
