# Generated by Django 4.2.8 on 2023-12-14 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_menu_employeemaster_api_user_employeemaster_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='icon',
            field=models.CharField(db_index=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='submenu',
            name='icon',
            field=models.CharField(db_index=True, max_length=100, null=True),
        ),
    ]
