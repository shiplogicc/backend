# Generated by Django 4.2.8 on 2023-12-20 16:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0008_alter_pincode_updated_by'),
        ('authentication', '0014_passwordresetotp'),
        ('slconfig', '0003_addonservices'),
        ('servicecenter', '0003_shipmentservices'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentHistory_2024_01',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(blank=True, db_index=True, default=0, null=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('expected_dod', models.DateTimeField(blank=True, null=True)),
                ('scan_push_status', models.SmallIntegerField(blank=True, db_index=True, default=0, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('scan_pushed_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('current_sc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_sc_hist_2024_01', to='location.servicecenter')),
                ('employee_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster')),
                ('reason_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.shipmentstatusmaster')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicecenter.shipment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShipmentHistory_2023_12',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(blank=True, db_index=True, default=0, null=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('expected_dod', models.DateTimeField(blank=True, null=True)),
                ('scan_push_status', models.SmallIntegerField(blank=True, db_index=True, default=0, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('scan_pushed_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('current_sc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_sc_hist_2023_12', to='location.servicecenter')),
                ('employee_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster')),
                ('reason_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.shipmentstatusmaster')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicecenter.shipment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
