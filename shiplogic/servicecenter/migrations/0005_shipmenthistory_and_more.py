# Generated by Django 4.2.8 on 2023-12-22 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slconfig', '0003_addonservices'),
        ('authentication', '0014_passwordresetotp'),
        ('servicecenter', '0004_shipmenthistory_2024_01_shipmenthistory_2023_12'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(blank=True, db_index=True, default=0, null=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('expected_dod', models.DateTimeField(blank=True, null=True)),
                ('scan_push_status', models.SmallIntegerField(blank=True, db_index=True, default=0, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('scan_pushed_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('employee_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster')),
                ('reason_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.shipmentstatusmaster')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicecenter.shipment')),
            ],
        ),
        migrations.RemoveField(
            model_name='shipmenthistory_2024_01',
            name='current_sc',
        ),
        migrations.RemoveField(
            model_name='shipmenthistory_2024_01',
            name='employee_code',
        ),
        migrations.RemoveField(
            model_name='shipmenthistory_2024_01',
            name='reason_code',
        ),
        migrations.RemoveField(
            model_name='shipmenthistory_2024_01',
            name='shipment',
        ),
        migrations.DeleteModel(
            name='ShipmentHistory_2023_12',
        ),
        migrations.DeleteModel(
            name='ShipmentHistory_2024_01',
        ),
    ]
