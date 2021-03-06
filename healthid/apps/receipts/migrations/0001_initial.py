# Generated by Django 2.1.7 on 2019-04-03 13:21

from django.db import migrations, models
import django.db.models.deletion
import healthid.utils.app_utils.id_generator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('outlets', '0002_auto_20190329_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldSet',
            fields=[
                ('id', models.CharField(default=healthid.utils.app_utils.id_generator.id_gen,
                                        editable=False, max_length=9, primary_key=True, serialize=False)),
                ('cashier', models.CharField(default='Served by:', max_length=244)),
                ('change_due', models.CharField(
                    default='Change due:', max_length=244)),
                ('receipt_no', models.CharField(
                    default='Receipt no:', max_length=244)),
                ('receipt', models.CharField(default='Receipt:', max_length=244)),
                ('discount_total', models.CharField(
                    default='Subtotal:', max_length=244)),
                ('subtotal', models.CharField(default='Subtotal:', max_length=244)),
                ('total_tax', models.CharField(default='Tax:', max_length=244)),
                ('amount_to_pay', models.CharField(
                    default='Amount to pay:', max_length=244)),
                ('purchase_total', models.CharField(
                    default='Purchase total', max_length=244)),
                ('loyalty', models.CharField(default='Loyalty:', max_length=244)),
                ('loyalty_earned', models.CharField(
                    default='Loyalty earned on purchase:', max_length=244)),
                ('loyalty_balance', models.CharField(
                    default='Current Loyalty Balance:', max_length=244)),
                ('footer', models.CharField(
                    default='Thank you for shopping with us.', max_length=244)),
            ],
        ),
        migrations.CreateModel(
            name='ReceiptTemplate',
            fields=[
                ('id', models.CharField(default=healthid.utils.app_utils.id_generator.id_gen,
                                        editable=False, max_length=9, primary_key=True, serialize=False)),
                ('cashier', models.BooleanField(default=True)),
                ('discount_total', models.BooleanField(default=True)),
                ('receipt_no', models.BooleanField(default=True)),
                ('receipt', models.BooleanField(default=True)),
                ('subtotal', models.BooleanField(default=True)),
                ('total_tax', models.BooleanField(default=True)),
                ('amount_to_pay', models.BooleanField(default=True)),
                ('purchase_total', models.BooleanField(default=True)),
                ('change_due', models.BooleanField(default=True)),
                ('loyalty', models.BooleanField(default=True)),
                ('loyalty_earned', models.BooleanField(default=True)),
                ('loyalty_balance', models.BooleanField(default=True)),
                ('barcode', models.BooleanField(default=True)),
                ('outlet', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='outlets.Outlet')),
            ],
        ),
        migrations.AddField(
            model_name='fieldset',
            name='receipt_template',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='receipts.ReceiptTemplate'),
        ),
    ]
