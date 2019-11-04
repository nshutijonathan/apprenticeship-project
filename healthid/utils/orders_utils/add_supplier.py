import csv

from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models.suppliers import PaymentTerms, Suppliers, Tier
from healthid.apps.outlets.models import City, Country
from healthid.utils.app_utils.validators import validate_mobile
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class AddSupplier:
    def handle_csv_upload(self, user, io_string):
        """
        This CSV method loops through the csv file populating the DB with
        the information in the csv rows through the SaveContextManager,
        :param io_string:
        :return total number csv rows uploaded into the DB:
        The columns of the csv file must be in a PARTICULAR order to ease
        the upload process
        The exact ordering expected of the csv would be:
        Column [0] -> name
        Column [1] -> email
        Column [2] -> mobile_number
        Column [3] -> country
        Column [4] -> address_line_1
        Column [5] -> address_line_2
        Column [6] -> lga
        Column [7] -> city
        Column [8] -> tier
        Column [9] -> logo
        Column [10] -> commentary
        Column [11] -> payment_terms
        Column [12] -> credit_days
        """

        params = {'model': Suppliers, 'error_type': ValidationError}
        supplier_count = 0
        for column in csv.reader(io_string):
            if len(column) < 13:
                raise ValidationError(ERROR_RESPONSES['csv_missing_field'])
            elif len(column) > 13:
                raise ValidationError(ERROR_RESPONSES['csv_many_field'])
            for idx in range(5):
                if column[idx] in (None, ''):
                    raise ValidationError(ERROR_RESPONSES['csv_field_error'])
            if column[7] in (None, '') or column[8] in (None, ''):
                raise ValidationError(ERROR_RESPONSES['csv_field_error'])
            if column[1] not in (
                    Suppliers.objects.values_list('email', flat=True)):
                # Makes calls to the DB to retrieve all emails
                # for checking duplication and skips over them
                # in the csv upload since emails should be unique.

                city = get_model_object(
                    City, 'name', column[7], error_type=NotFound)
                country = get_model_object(
                    Country, 'name',
                    column[3].title(), error_type=NotFound)
                tier = get_model_object(
                    Tier, 'name', column[8], error_type=NotFound)
                user_id = get_model_object(
                    User, 'id', user.pk, error_type=NotFound)

                credit_days = int(column[12])
                if credit_days == 0:
                    payment_terms = get_model_object(
                        PaymentTerms, 'name',
                        'cash on delivery', error_type=NotFound)
                else:
                    payment_terms = get_model_object(
                        PaymentTerms, 'name', 'on credit', error_type=NotFound)
                if city.country.name != country.name:
                    raise ValidationError(
                        ERROR_RESPONSES['country_city_mismatch']
                        .format(country.name, city.name))
                phone_number = validate_mobile(column[2])
                suppliers_instance = Suppliers(
                    name=column[0],
                    email=column[1],
                    mobile_number=phone_number,
                    country=country,
                    address_line_1=column[4],
                    address_line_2=column[5],
                    lga=column[6],
                    city=city,
                    tier=tier,
                    logo=column[9],
                    commentary=column[10],
                    payment_terms=payment_terms,
                    credit_days=credit_days,
                    user=user_id,
                )

                outlet = check_user_has_an_active_outlet(user)
                with SaveContextManager(suppliers_instance,
                                        **params) as supplier:
                    supplier.outlet.add(outlet)
                    pass
                supplier_count += 1
        return supplier_count
