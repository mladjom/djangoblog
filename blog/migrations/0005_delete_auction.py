# Generated by Django 5.1.4 on 2025-01-06 05:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0004_auction"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Auction",
        ),
    ]
