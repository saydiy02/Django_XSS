# Generated by Django 5.0.4 on 2024-06-09 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suggestxss', '0004_userdata_created_at_userdata_updated_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdata',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='userdata',
            name='updated_at',
        ),
    ]