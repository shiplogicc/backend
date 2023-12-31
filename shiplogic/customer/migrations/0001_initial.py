# Generated by Django 4.2.8 on 2023-12-13 11:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0008_alter_otpconfig_without_otp'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0002_remove_areamaster_added_on_remove_areamaster_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=30)),
                ('activation_status', models.BooleanField(blank=True)),
                ('activation_date', models.DateField(blank=True, null=True)),
                ('contract_from', models.DateField()),
                ('contract_to', models.DateField()),
                ('billing_schedule', models.IntegerField(default=7, max_length=3)),
                ('day_of_billing', models.SmallIntegerField(default=7)),
                ('remittance_cycle', models.SmallIntegerField(default=7)),
                ('credit_limit', models.IntegerField(default=10000, max_length=10)),
                ('credit_period', models.IntegerField(default=10, max_length=3)),
                ('fuel_surcharge_applicable', models.BooleanField(blank=True, default=True)),
                ('to_pay_charge', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('vchc_rate', models.DecimalField(decimal_places=2, default=0.5, max_digits=4)),
                ('vchc_min', models.DecimalField(decimal_places=2, default=0.5, max_digits=6)),
                ('vchc_min_amnt_applied', models.IntegerField(default=5000, max_length=5)),
                ('return_to_origin', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('flat_cod_amt', models.IntegerField(blank=True, max_length=4, null=True)),
                ('demarrage_min_amt', models.IntegerField(blank=True, max_length=4, null=True)),
                ('demarrage_perkg_amt', models.IntegerField(blank=True, max_length=4, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('pan_number', models.CharField(blank=True, max_length=20, null=True)),
                ('tan_number', models.CharField(blank=True, max_length=20, null=True)),
                ('website', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('bill_delivery_email', models.BooleanField(default=True)),
                ('bill_delivery_hand', models.BooleanField(default=True)),
                ('invoice_date', models.DateField(blank=True, null=True)),
                ('next_bill_date', models.DateField(blank=True, null=True)),
                ('reverse_charges', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('referred_by', models.CharField(blank=True, max_length=30, null=True)),
                ('activation_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activation_by', to=settings.AUTH_USER_MODEL)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.address2')),
            ],
        ),
        migrations.CreateModel(
            name='Legality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legality_type', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='NamedUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authentication.employeemaster',),
        ),
        migrations.CreateModel(
            name='Shipper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias_code', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.IntegerField(choices=[(0, 'Normal'), (1, 'To Pay')], default=0)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.address')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerAPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='API username', max_length=50)),
                ('password', models.CharField(help_text='API Password', max_length=24)),
                ('ipaddress', models.CharField(default=0, help_text='comma separated IP address', max_length=255)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='approved',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approver', to='customer.nameduser'),
        ),
        migrations.AddField(
            model_name='customer',
            name='authorized',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authorizer', to='customer.nameduser'),
        ),
        migrations.AddField(
            model_name='customer',
            name='contact_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.contact'),
        ),
        migrations.AddField(
            model_name='customer',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customer',
            name='decision_maker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decision_maker', to='location.contact'),
        ),
        migrations.AddField(
            model_name='customer',
            name='legality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.legality'),
        ),
        migrations.AddField(
            model_name='customer',
            name='saleslead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='saleslead', to='customer.nameduser'),
        ),
        migrations.AddField(
            model_name='customer',
            name='signed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='signatory', to='customer.nameduser'),
        ),
        migrations.AddField(
            model_name='customer',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customer',
            name='zone_label',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.zonelabel'),
        ),
    ]
