from graphql import GraphQLError
from healthid.apps.orders.models import Suppliers
from healthid.apps.products.models import (MeasurementUnit, Product,
                                           ProductCategory)


def handle_validation(**kwargs):
    product_exists = Product.objects.filter(
        product_name=kwargs.get('product_name')).first()
    if product_exists:
        raise GraphQLError("Product with productname {} already exists".format(
            product_exists))

    if kwargs.get('product_category_id'):
        product_category_id = ProductCategory.objects.filter(
            id=kwargs.get('product_category_id')).first()
        if not product_category_id:
            raise GraphQLError(
                "product category with  id {} doesnot exist".format(
                    kwargs['product_category_id'])
                )

    if kwargs.get('measurement_unit_id'):
        measurement_unit_id = MeasurementUnit.objects.filter(
            id=kwargs.get('measurement_unit_id')).first()
        if not measurement_unit_id:
            raise GraphQLError(
                f"""
                Measuremnt unit id {kwargs['measurement_unit_id']}\t
                doesnot exist
                """
            )

    if kwargs.get('prefered_supplier_id'):
        prefered_supplier_id = Suppliers.objects.filter(
            id=kwargs['prefered_supplier_id']).first()
        if not prefered_supplier_id:
            raise GraphQLError(
                f"supplier id {kwargs['prefered_supplier_id']} doesnot exist")

    if kwargs.get('backup_supplier_id'):
        backup_supplier_id = Suppliers.objects.filter(
            id=kwargs['backup_supplier_id']).first()
        if not backup_supplier_id:
            raise GraphQLError(
                f"supplier id  {kwargs['backup_supplier_id']} doesnot exist")
