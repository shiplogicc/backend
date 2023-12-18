# Generated by Django 4.2.8 on 2023-12-11 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0005_department_employeemaster_usertype_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(blank=True, default='', max_length=100)),
                ('address3', models.CharField(blank=True, default='', max_length=100)),
                ('address4', models.CharField(blank=True, default='', max_length=100)),
                ('pincode', models.CharField(blank=True, default='', max_length=15)),
                ('phone', models.CharField(blank=True, default='', max_length=100)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Address2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(blank=True, default='', max_length=100)),
                ('address3', models.CharField(blank=True, default='', max_length=100)),
                ('address4', models.CharField(blank=True, default='', max_length=100)),
                ('city', models.CharField(blank=True, default='', max_length=100)),
                ('state', models.CharField(blank=True, default='', max_length=100)),
                ('pincode', models.CharField(blank=True, default='', max_length=100)),
                ('phone', models.CharField(blank=True, default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=30)),
                ('city_shortcode', models.CharField(max_length=30)),
                ('city_type', models.SmallIntegerField(default=0)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CityCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=30)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('designation', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('address1', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('address2', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('address3', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('address4', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, default='', max_length=15, null=True)),
                ('phone', models.CharField(blank=True, default='', max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True, default='0000-00-00', null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.city')),
            ],
        ),
        migrations.CreateModel(
            name='DcLocalityMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locality', models.CharField(db_index=True, max_length=255)),
                ('dc_shortcode', models.CharField(db_index=True, max_length=20)),
                ('length', models.CharField(max_length=10)),
                ('city_shortcode', models.CharField(db_index=True, max_length=20)),
                ('state_shortcode', models.CharField(db_index=True, max_length=20)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('status', models.IntegerField(db_index=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pincode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pincode', models.IntegerField()),
                ('area', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('status', models.IntegerField(default=1, max_length=1)),
                ('sdl', models.IntegerField(default=0, help_text='Special Delivery Location. 0 is no and 1 is yes', max_length=1)),
                ('date_of_discontinuance', models.DateTimeField(blank=True, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('org_cluster', models.CharField(blank=True, default='', max_length=6, null=True)),
                ('dest_cluster', models.CharField(blank=True, default='', max_length=6, null=True)),
                ('route', models.CharField(blank=True, max_length=20, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.city')),
            ],
        ),
        migrations.CreateModel(
            name='PincodeEmbargoBehaviour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pincode_status', models.IntegerField(db_index=True, default=0)),
                ('g1_behaviour', models.IntegerField(db_index=True, default=0)),
                ('g2_behaviour', models.IntegerField(db_index=True, default=0)),
                ('g3_behaviour', models.IntegerField(db_index=True, default=0)),
                ('status_description', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('activation_status', models.BooleanField(db_index=True, default=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PinRoutes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pinroute_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_name', models.CharField(max_length=30)),
                ('region_shortcode', models.CharField(max_length=20)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('center_name', models.CharField(max_length=30)),
                ('center_shortcode', models.CharField(max_length=30)),
                ('type', models.IntegerField(choices=[(0, 'Service Centre'), (1, 'Hub'), (2, 'Head Quarter'), (3, 'Processing Centre')], default=0, max_length=1)),
                ('status', models.IntegerField(db_index=True, default=1)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.address')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.city')),
                ('contact', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.contact')),
            ],
            options={
                'ordering': ['center_shortcode'],
            },
        ),
        migrations.CreateModel(
            name='SorterPincode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pincode', models.IntegerField()),
                ('service_center', models.IntegerField(max_length=10)),
                ('pickup_sc', models.IntegerField(blank=True, db_index=True, max_length=10, null=True)),
                ('return_sc', models.IntegerField(blank=True, db_index=True, max_length=10, null=True)),
                ('pin_route', models.IntegerField(blank=True, db_index=True, max_length=10, null=True)),
                ('area', models.CharField(blank=True, db_index=True, default='', max_length=255, null=True)),
                ('status', models.IntegerField(db_index=True, default=1, max_length=1)),
                ('Sorter_push_status', models.IntegerField(db_index=True, default=1, max_length=1)),
                ('Sorter_push_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('sdl', models.IntegerField(default=0, help_text='Special Delivery Location. 0 is no and 1 is yes', max_length=1)),
                ('date_of_discontinuance', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('city', models.IntegerField(blank=True, db_index=True, null=True)),
                ('zone', models.IntegerField(blank=True, db_index=True, null=True)),
                ('kyc_sc', models.IntegerField(blank=True, db_index=True, null=True)),
                ('org_cluster', models.CharField(blank=True, db_index=True, default='', max_length=6, null=True)),
                ('dest_cluster', models.CharField(blank=True, db_index=True, default='', max_length=6, null=True)),
                ('reverse_sc', models.IntegerField(blank=True, db_index=True, null=True)),
                ('route', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('updated_by', models.IntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_name', models.CharField(max_length=30)),
                ('state_shortcode', models.CharField(max_length=20)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ZoneLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_name', models.CharField(max_length=30)),
                ('zone_shortcode', models.CharField(max_length=20)),
                ('code', models.CharField(blank=True, max_length=2, null=True)),
                ('location_type', models.SmallIntegerField(choices=[(0, 'Regular Location'), (1, 'UP Location')], default=0, max_length=1)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.zonelabel')),
            ],
        ),
        migrations.CreateModel(
            name='StateAdditionalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_info_key', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('add_info_value', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('activation_status', models.BooleanField(db_index=True, default=True)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.state')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceCenterAdditionalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_info_key', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('add_info_value', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('activation_status', models.BooleanField(db_index=True, default=True)),
                ('sc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.servicecenter')),
            ],
        ),
        migrations.CreateModel(
            name='PincodeEmbargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('activation_status', models.BooleanField(db_index=True, default=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, null=True)),
                ('pincode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.pincode')),
            ],
        ),
        migrations.CreateModel(
            name='PincodeAdditionalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_info_key', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('add_info_value', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('activation_status', models.BooleanField(db_index=True, default=True)),
                ('pincode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.pincode')),
            ],
        ),
        migrations.AddField(
            model_name='pincode',
            name='pickup_sc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pickup', to='location.servicecenter'),
        ),
        migrations.AddField(
            model_name='pincode',
            name='pin_route',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.pinroutes'),
        ),
        migrations.AddField(
            model_name='pincode',
            name='return_sc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='return_sc', to='location.servicecenter'),
        ),
        migrations.AddField(
            model_name='pincode',
            name='reverse_sc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reverse_sc', to='location.servicecenter'),
        ),
        migrations.AddField(
            model_name='pincode',
            name='service_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.servicecenter'),
        ),
        migrations.AddField(
            model_name='pincode',
            name='updated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster'),
        ),
        migrations.AddField(
            model_name='pincode',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.zone'),
        ),
        migrations.CreateModel(
            name='DcLocalityMasterChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locality', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('dc_shortcode', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('length', models.CharField(blank=True, db_index=True, max_length=10, null=True)),
                ('city_shortcode', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('state_shortcode', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('status', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('dclocality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.dclocalitymaster')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster')),
            ],
        ),
        migrations.AddField(
            model_name='contact',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.state'),
        ),
        migrations.AddField(
            model_name='city',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.citycategory'),
        ),
        migrations.AddField(
            model_name='city',
            name='labeled_zones',
            field=models.ManyToManyField(related_name='label_city', to='location.zone'),
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.region'),
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.state'),
        ),
        migrations.AddField(
            model_name='city',
            name='zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.zone'),
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch_name', models.CharField(max_length=30)),
                ('branch_shortcode', models.CharField(max_length=30)),
                ('branch_type', models.CharField(choices=[('HeadOffice', 'HeadOffice'), ('Branch', 'Branch')], default=1, max_length=13)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.city')),
            ],
        ),
        migrations.CreateModel(
            name='AreaMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(max_length=30)),
                ('area_shortcode', models.CharField(max_length=30)),
                ('status', models.IntegerField(db_index=True, default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.branch')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.city')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.city'),
        ),
        migrations.AddField(
            model_name='address',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.state'),
        ),
        migrations.CreateModel(
            name='HubServiceCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=0)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hub_hubsc', to='location.servicecenter')),
                ('sc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sc_hubsc', to='location.servicecenter')),
            ],
            options={
                'unique_together': {('hub', 'sc')},
            },
        ),
    ]
