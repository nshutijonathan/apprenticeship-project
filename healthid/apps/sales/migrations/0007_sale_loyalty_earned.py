# Generated by Django 2.1.7 on 2019-06-26 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_sale_saledetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='loyalty_earned',
            field=models.PositiveIntegerField(default=0),
        ),
    ]