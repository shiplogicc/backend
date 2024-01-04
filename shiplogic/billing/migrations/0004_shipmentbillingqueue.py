# Generated by Django 4.2.8 on 2023-12-26 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentBillingQueue',
            fields=[
                ('airwaybill_number', models.BigIntegerField(db_index=True, primary_key=True, serialize=False)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('shipment_date', models.DateTimeField(db_index=True)),
                ('shipment_type', models.IntegerField(db_index=True, default=0)),
                ('updated_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]