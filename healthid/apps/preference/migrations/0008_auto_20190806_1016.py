# Generated by Django 2.1.7 on 2019-08-06 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preference', '0007_auto_20190723_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesspreference',
            name='returnable_days',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='outletpreference',
            name='returnable_days',
            field=models.IntegerField(default=30),
        ),
    ]
