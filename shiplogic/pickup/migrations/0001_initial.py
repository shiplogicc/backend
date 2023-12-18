# Generated by Django 4.2.8 on 2023-12-15 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('slconfig', '0001_initial'),
        ('authentication', '0013_alter_role_usertype'),
        ('customer', '0001_initial'),
        ('location', '0003_pincodevirtualdcmapping_adhoccitymapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pieces', models.IntegerField(blank=True, default=0, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(blank=True, default=0, null=True)),
                ('pickup_date', models.DateField()),
                ('pickup_time', models.TimeField(blank=True, null=True)),
                ('customer_name', models.CharField(max_length=150)),
                ('address_line1', models.CharField(max_length=150)),
                ('address_line2', models.CharField(blank=True, max_length=150, null=True)),
                ('address_line3', models.CharField(blank=True, max_length=150, null=True)),
                ('address_line4', models.CharField(blank=True, max_length=150, null=True)),
                ('pincode', models.CharField(blank=True, max_length=15, null=True)),
                ('mobile', models.BigIntegerField(blank=True, null=True)),
                ('telephone', models.CharField(blank=True, max_length=100, null=True)),
                ('caller_name', models.CharField(blank=True, max_length=50, null=True)),
                ('to_pay', models.BooleanField(default=False)),
                ('reverse_pickup', models.BooleanField(default=False)),
                ('regular_pickup', models.BooleanField(default=False)),
                ('callers_number', models.BigIntegerField(blank=True, null=True)),
                ('email', models.CharField(blank=True, max_length=150, null=True)),
                ('office_close_time', models.TimeField(blank=True, null=True)),
                ('product_code', models.CharField(blank=True, max_length=50, null=True)),
                ('actual_weight', models.FloatField(blank=True, default=0, null=True)),
                ('volume_weight', models.FloatField(blank=True, default=0, null=True)),
                ('pickup_route', models.IntegerField(blank=True, default=0, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('reminder', models.CharField(blank=True, max_length=200, null=True)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.areamaster')),
                ('customer_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
                ('mode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.mode')),
                ('return_subcustomer_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='return_subcustomer_code', to='customer.shipper')),
                ('service_centre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.servicecenter')),
                ('subcustomer_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.shipper')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReversePickupRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_date', models.DateField()),
                ('pickup_time', models.TimeField(blank=True, null=True)),
                ('pincode', models.CharField(blank=True, max_length=15, null=True)),
                ('mobile', models.BigIntegerField(blank=True, null=True)),
                ('reverse_pickup', models.BooleanField(default=True)),
                ('status', models.IntegerField(blank=True, default=0, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster')),
                ('customer_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
                ('pickup', models.ManyToManyField(blank=True, null=True, to='pickup.pickupregistration')),
            ],
        ),
    ]
