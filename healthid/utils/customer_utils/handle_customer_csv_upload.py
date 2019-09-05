import csv
from rest_framework.exceptions import NotFound, ValidationError
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.profiles.models import Profile
from healthid.apps.outlets.models import Country, City


class HandleCustomerCSVValidation:
    def handle_customer_csv_upload(self, io_string):
        """
        This CSV method loops through the csv file populating the DB with
        the information in the csv rows through the SaveContextManager,
        :param io_string:
        :return total number pf csv rows uploaded into the DB:
        The columns of the csv file must be in a PARTICULAR order to ease
        the upload process
        The exact ordering expected of the csv would be:
        Column [0] -> email
        Column [1] -> first_name
        Column [2] -> last_name
        Column [3] -> primary_mobile_number
        Column [4] -> secondary_mobile_number
        Column [5] -> address_line_1
        Column [6] -> address_line_2
        Column [7] -> local_government_area
        Column [8] -> city
        Column [9] -> country
        Column [10] -> emergency_contact_name
        Column [11] -> emergency_contact_number
        Column [12] -> emergency_contact_email
        Column [13] -> loyalty_member
        Column [14] -> loyalty_points
        """
        params = {'model': Profile, 'error_type': ValidationError}
        customer_count = 0
        # Makes single call to the DB to retrieve all emails
        # for checking duplication
        # in the csv upload since emails should be unique.
        customer_emails = Profile.objects.values_list('email', flat=True)

        for row in csv.reader(io_string):

            if len(row) < 14:
                message = {"error": "csv file missing column(s)"}
                raise ValidationError(message)

            country = get_model_object(
                Country, 'name', row[9], error_type=NotFound)
            city = get_model_object(
                City, 'name', row[8], error_type=NotFound)

            if row[0] not in customer_emails:
                # Checks for duplications and skips over them
                customer_profile_instance = Profile(
                    first_name=row[1],
                    last_name=row[2],
                    email=row[0],
                    city=city,
                    country=country,
                    primary_mobile_number=row[3],
                    secondary_mobile_number=row[4],
                    loyalty_member=row[13],
                    loyalty_points=row[14],
                    local_government_area=row[7],
                    address_line_1=row[5],
                    address_line_2=row[6],
                    emergency_contact_name=row[10],
                    emergency_contact_number=row[11],
                    emergency_contact_email=row[12])

                with SaveContextManager(customer_profile_instance, **params):
                    pass

                customer_count += 1

        return customer_count
