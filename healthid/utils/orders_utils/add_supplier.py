import csv

from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models.suppliers import PaymentTerms, Suppliers, Tier
from healthid.apps.outlets.models import City
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
        Column [3] -> rating
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
        # Makes single call to the DB to retrieve all emails
        # for checking duplication
        # in the csv upload since emails should be unique.
        suppliers_info = Suppliers.objects.values_list('email', flat=True)

        for column in csv.reader(io_string):
            if len(column) < 13:
                raise ValidationError(ERROR_RESPONSES['csv_missing_field'])
            elif len(column) > 13:
                raise ValidationError(ERROR_RESPONSES['csv_many_field'])

            if (column[1] not in suppliers_info or column[1]):
                # Checks for duplications and skips over them

                city = get_model_object(
                    City, 'name', column[7], error_type=NotFound)
                tier = get_model_object(
                    Tier, 'name', column[8], error_type=NotFound)
                payment_terms = get_model_object(
                    PaymentTerms, 'name', column[11], error_type=NotFound)
                user_id = get_model_object(
                    User, 'id', user.pk, error_type=NotFound)

                suppliers_instance = Suppliers(
                    name=column[0],
                    email=column[1],
                    mobile_number=column[2],
                    rating=column[3],
                    address_line_1=column[4],
                    address_line_2=column[5],
                    lga=column[6],
                    city=city,
                    tier=tier,
                    logo=column[9],
                    commentary=column[10],
                    payment_terms=payment_terms,
                    credit_days=column[12],
                    user=user_id,
                )

                outlet = check_user_has_an_active_outlet(user)
                with SaveContextManager(suppliers_instance,
                                        **params) as supplier:
                    supplier.outlet.add(outlet)
                    pass
                supplier_count += 1
        return supplier_count
