from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models.suppliers import PaymentTerms, Suppliers, Tier
from healthid.apps.outlets.models import City, Country
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.orders_utils.validate_suppliers_csv_upload import\
    validate_suppliers_csv_upload


class AddSupplier:
    def handle_csv_upload(self, user, io_string):
        """
        This CSV method loops through the csv file populating the DB with
        the information in the csv rows through the SaveContextManager,
        :param io_string:
        :return total number csv rows uploaded into the DB:
        """

        params = {'model': Suppliers, 'error_type': ValidationError}
        [supplier_count, row_count] = [0, 0]
        duplicated_suppliers = []
        suppliers = validate_suppliers_csv_upload(io_string)

        for row in suppliers:
            row_count += 1
            if row['email'] not in (
                    Suppliers.objects.values_list('email', flat=True)):

                city = get_model_object(City,
                                        'name__iexact',
                                        row['city'],
                                        error_type=NotFound,
                                        label='name')
                country = get_model_object(Country,
                                           'name__iexact',
                                           row['country'],
                                           error_type=NotFound,
                                           label='name')
                tier = get_model_object(Tier,
                                        'name__iexact',
                                        row['tier'],
                                        error_type=NotFound,
                                        label='name')
                user_id = get_model_object(User,
                                           'id',
                                           user.pk,
                                           error_type=NotFound)

                credit_days = int(row['credit days'] or 0)
                payment_terms = get_model_object(PaymentTerms,
                                                 'name__iexact',
                                                 row['payment terms'],
                                                 error_type=NotFound,
                                                 label='name')

                # check payment_terms
                if credit_days == 0 and row['payment terms'] == 'on credit':
                    raise ValidationError(
                        ERROR_RESPONSES['payment_terms'].format(row_count))

                if city.country.name != country.name:
                    raise ValidationError(
                        ERROR_RESPONSES['country_city_mismatch']
                        .format(country.name, city.name))

                suppliers_instance = Suppliers(
                    name=row['name'],
                    email=row['email'],
                    mobile_number=row['mobile number'],
                    country=country,
                    address_line_1=row['address line 1'],
                    address_line_2=row['address line 2'],
                    lga=row['lga'],
                    city=city,
                    tier=tier,
                    logo=row['logo'],
                    commentary=row['commentary'],
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
            else:
                duplicated_suppliers.append(
                    ERROR_RESPONSES['duplication_error'].format(row['email']))
        return {'supplier_count': supplier_count,
                'duplicated_suppliers': duplicated_suppliers}
