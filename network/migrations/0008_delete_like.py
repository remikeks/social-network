# Generated by Django 4.1.6 on 2023-06-05 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_remove_post_liked_post_liked_by'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Like',
        ),
    ]
