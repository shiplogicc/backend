# Generated by Django 4.2.8 on 2023-12-15 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('freight_charge', models.FloatField(blank=True, default=0, null=True)),
                ('sdl_charge', models.FloatField(blank=True, default=0, null=True)),
                ('fuel_surcharge', models.FloatField(blank=True, default=0, null=True)),
                ('valuable_cargo_handling_charge', models.FloatField(blank=True, default=0, null=True)),
                ('to_pay_charge', models.FloatField(blank=True, default=0, null=True)),
                ('rto_charge', models.FloatField(blank=True, default=0, null=True)),
                ('demarrage_charge', models.FloatField(blank=True, default=0, null=True)),
                ('cod_applied_charge', models.FloatField(blank=True, default=0, null=True)),
                ('cod_subtract_charge', models.FloatField(blank=True, default=0, null=True)),
                ('total_cod_charge', models.FloatField(blank=True, default=0, null=True)),
                ('billing_date', models.DateField(blank=True, null=True)),
                ('billing_date_from', models.DateField(blank=True, null=True)),
                ('generation_status', models.IntegerField(default=0, max_length=1)),
                ('payment_status', models.IntegerField(default=0, max_length=1)),
                ('service_tax', models.FloatField(blank=True, default=0, null=True)),
                ('education_secondary_tax', models.FloatField(blank=True, default=0, null=True)),
                ('cess_higher_secondary_tax', models.FloatField(blank=True, default=0, null=True)),
                ('bill_generation_date', models.DateTimeField(blank=True, null=True)),
                ('total_charge_pretax', models.FloatField(blank=True, default=0, null=True)),
                ('total_payable_charge', models.FloatField(blank=True, default=0, null=True)),
                ('balance', models.FloatField(blank=True, default=0, null=True)),
                ('received', models.FloatField(blank=True, default=0, null=True)),
                ('adjustment', models.FloatField(blank=True, default=0, null=True)),
                ('adjustment_cr', models.FloatField(blank=True, default=0, null=True)),
                ('sdd_charge', models.FloatField(blank=True, default=0, null=True)),
                ('reverse_charge', models.FloatField(blank=True, default=0, null=True)),
                ('shipment_count', models.FloatField(blank=True, default=0, null=True)),
                ('total_chargeable_weight', models.FloatField(blank=True, default=0, null=True)),
                ('billing_type', models.SmallIntegerField(default=0)),
                ('bill_number', models.CharField(db_index=True, default='', max_length=25)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
        ),
    ]
