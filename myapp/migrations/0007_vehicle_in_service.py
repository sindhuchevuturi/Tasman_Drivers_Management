# Generated by Django 5.1.3 on 2024-11-20 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_trailer_in_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='in_service',
            field=models.BooleanField(default=False),
        ),
    ]