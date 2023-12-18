# Generated by Django 4.2.8 on 2023-12-15 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('location', '0002_remove_areamaster_added_on_remove_areamaster_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PincodeVirtualDCMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activation_status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('pincode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.pincode')),
                ('virtual_dc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='virtual_dc', to='location.servicecenter')),
            ],
        ),
        migrations.CreateModel(
            name='AdhocCityMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activation_status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adhoc_customer', to='customer.customer')),
                ('destination_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adhoc_dest_city', to='location.city')),
                ('origin_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adhoc_origin_city', to='location.city')),
            ],
        ),
    ]
