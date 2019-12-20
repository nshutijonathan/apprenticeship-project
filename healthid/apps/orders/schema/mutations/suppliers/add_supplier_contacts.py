import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.schema.suppliers_query import (SuppliersContactsType)
from healthid.apps.orders.models import SuppliersContacts
from healthid.utils.app_utils.database import (SaveContextManager)
from healthid.utils.app_utils.validator import validator


class SuppliersContactsInput(graphene.InputObjectType):
    supplier_id = graphene.String(required=True)
    email = graphene.String()
    mobile_number = graphene.String()
    address_line_1 = graphene.String()
    address_line_2 = graphene.String()
    lga = graphene.String()
    city_id = graphene.Int()
    country_id = graphene.Int()


class AddSupplierContacts(graphene.Mutation):
    """
    Add contacts of a supplier to the database

    args:
        supplier_id(str): supplier ID
        email(str): supplier contact email
        mobile_number(str): contact number
        address_line_1(str): first address line
        address_line_2(str): second address line
        lga(str): name of the supplier's local government area
        city_id(int): id of the supplier city location
        country_id(int): supplier country

    returns:
        supplier_contacts(obj): 'SuppliersContacts' model object
                                detailing the created supplier contacts.
    """

    class Arguments:
        input = SuppliersContactsInput(required=True)

    supplier_contacts = graphene.Field(SuppliersContactsType)

    @classmethod
    def validate_fields(cls, input):
        fields = input
        fields['email'] = validator.validate_email(
            input['email']) if input.get('email') else None
        fields['mobile_number'] = validator.validate_mobile(
            input.mobile_number)
        fields['lga'] = input['lga'].strip() if input.get('lga') else None
        fields['address_line_1'] = input['address_line_1'].strip(
        ) if input.get('address_line_1') else None
        fields['address_line_2'] = input['address_line_2'].strip(
        ) if input.get('address_line_2') else None
        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, input=None):
        supplier_contacts = SuppliersContacts()
        fields = cls.validate_fields(input)

        for (key, value) in fields.items():
            setattr(supplier_contacts, key, value)
        with SaveContextManager(supplier_contacts,
                                model=SuppliersContacts) as supplier_contacts:
            return cls(supplier_contacts=supplier_contacts)
