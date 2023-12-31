# Generated by Django 4.2.8 on 2023-12-27 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0015_alter_employeemaster_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='JsonSchema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('schema', models.JSONField()),
            ],
        ),
        migrations.AlterField(
            model_name='employeemaster',
            name='mobile_no',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
