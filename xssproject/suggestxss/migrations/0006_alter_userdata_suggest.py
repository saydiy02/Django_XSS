# Generated by Django 5.0.4 on 2024-06-23 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggestxss', '0005_remove_userdata_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='suggest',
            field=models.IntegerField(choices=[(0, 'Nmap & PwnXSS'), (1, 'Nmap & XSStrike')]),
        ),
    ]