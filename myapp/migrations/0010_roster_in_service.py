# Generated by Django 5.1.3 on 2024-11-26 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_auto_20241126_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='in_service',
            field=models.BooleanField(default=False),
        ),
    ]
