# Generated by Django 5.0.4 on 2024-04-27 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0006_alter_samplehomework_base_homework_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="homework",
            name="is_published",
            field=models.BooleanField(default=False),
        ),
    ]
