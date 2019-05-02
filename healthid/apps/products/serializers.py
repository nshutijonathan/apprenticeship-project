from rest_framework import serializers

from healthid.apps.products.models import Product


class ProductsSerializer(serializers.ModelSerializer):
    product_category = serializers.CharField(source='product_category.name')
    measurement_unit = serializers.CharField(source='measurement_unit.name')
    prefered_supplier = serializers.CharField(source='prefered_supplier.name')
    backup_supplier = serializers.CharField(source='backup_supplier.name')

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_category', 'measurement_unit',
            'sku_number', 'description', 'brand', 'manufacturer', 'vat_status',
            'quality', 'sales_price', 'created_date', 'nearest_expiry_date',
            'prefered_supplier', 'backup_supplier', 'pre_tax_retail_price',
            'unit_cost', 'pack_size'
        ]
