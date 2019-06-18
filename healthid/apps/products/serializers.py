from rest_framework import serializers

from healthid.apps.products.models import Product


class ProductsSerializer(serializers.ModelSerializer):
    product_category = serializers.CharField(source='product_category.name')
    measurement_unit = serializers.CharField(source='measurement_unit.name')
    preferred_supplier = serializers.CharField(source='preferred_supplier.name')  # noqa
    backup_supplier = serializers.CharField(source='backup_supplier.name')

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_category', 'measurement_unit',
            'sku_number', 'description', 'brand', 'manufacturer', 'vat_status',
            'sales_price', 'created_date', 'nearest_expiry_date',
            'preferred_supplier', 'backup_supplier', 'pre_tax_retail_price',
            'unit_cost'
        ]
