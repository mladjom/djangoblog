# Generated by Django 5.1.4 on 2024-12-14 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_tag_meta_description_tag_meta_title"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tag",
            name="meta_title",
        ),
    ]
