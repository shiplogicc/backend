# Generated by Django 4.2.8 on 2023-12-28 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0017_role_sub_menu'),
        ('slconfig', '0003_addonservices'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallCentreComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('comments', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('employee_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.employeemaster')),
                ('shipments', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicecenter.shipment')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerNdrConcerns',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=150, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerNdrResolutionMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=150)),
                ('action_type', models.CharField(default='D', max_length=1)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('concern', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='track_me.customerndrconcerns')),
                ('reasoncode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.shipmentstatusmaster')),
            ],
        ),
        migrations.CreateModel(
            name='CallCentreCommentResolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('scheduled_delivery_date', models.DateField(blank=True, null=True)),
                ('fake_update', models.SmallIntegerField(default=0)),
                ('call_centre_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='track_me.callcentrecomment')),
                ('concern', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='track_me.customerndrconcerns')),
                ('reason_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slconfig.shipmentstatusmaster')),
                ('resolution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='track_me.customerndrresolutionmaster')),
                ('undelivered_reasoncode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_undelivered_reasoncode', to='slconfig.shipmentstatusmaster')),
            ],
        ),
    ]
