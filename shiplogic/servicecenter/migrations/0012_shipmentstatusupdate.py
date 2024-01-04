# Generated by Django 4.2.8 on 2023-12-29 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0008_alter_pincode_updated_by'),
        ('authentication', '0017_role_sub_menu'),
        ('slconfig', '0003_addonservices'),
        ('servicecenter', '0011_shipmenthistory_partition_month'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentStatusUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
                ('recieved_by', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.IntegerField(blank=True, default=0, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('ajax_field', models.CharField(blank=True, max_length=20, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('data_entry_emp_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statsupd_dataemp', to='authentication.employeemaster')),
                ('delivery_emp_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statsupd_deliveryemp', to='authentication.employeemaster')),
                ('origin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statsupd_origin', to='location.servicecenter')),
                ('reason_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.shipmentstatusmaster')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicecenter.shipment')),
            ],
        ),
    ]