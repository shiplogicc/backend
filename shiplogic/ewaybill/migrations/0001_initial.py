# Generated by Django 4.2.8 on 2023-12-20 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('servicecenter', '0002_apishipments_prefershipments'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentEwaybill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ewaybill', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipment_ewaybill', to='servicecenter.shipment')),
            ],
        ),
    ]
