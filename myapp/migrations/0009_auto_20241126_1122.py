# Generated by Django 5.1.3 on 2024-11-26 00:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_auto_20241121_0910'),
    ]

    operations = [
    ]
    operations = [
        migrations.RemoveField(
            model_name='roster',
            name='runsheet_received',
        ),
    ]