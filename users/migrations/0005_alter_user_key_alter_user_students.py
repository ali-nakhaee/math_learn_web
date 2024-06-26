# Generated by Django 5.0.4 on 2024-04-27 10:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="key",
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="students",
            field=models.ManyToManyField(
                blank=True, related_name="teachers", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
