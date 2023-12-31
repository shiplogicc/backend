# Generated by Django 4.2.8 on 2023-12-15 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAdditionalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, max_length=200, null=True)),
                ('add_info_key', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('add_info_value', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('added_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer', unique=True)),
            ],
        ),
    ]
