# Generated by Django 4.2.8 on 2023-12-16 05:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slconfig', '0002_holidaymaster'),
        ('customer', '0003_shippermapping'),
        ('location', '0003_pincodevirtualdcmapping_adhoccitymapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransitMasterGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='TransitMasterClusterBased',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.IntegerField(default=1, max_length=1)),
                ('cutoff_time', models.CharField(default='1900', max_length=5)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
                ('mode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slconfig.mode')),
                ('transit_master_dest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transit_master_dest_cm', to='location.transitmastergroup')),
                ('transit_master_orignal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transit_master_orignal_cm', to='location.transitmastergroup')),
            ],
        ),
    ]
