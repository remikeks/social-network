# Generated by Django 4.1.6 on 2023-05-18 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_user_followers_delete_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='liked',
            field=models.BooleanField(default=False),
        ),
    ]
