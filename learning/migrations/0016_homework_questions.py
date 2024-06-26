# Generated by Django 5.0.4 on 2024-05-06 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0015_remove_homework_questions"),
    ]

    operations = [
        migrations.AddField(
            model_name="homework",
            name="questions",
            field=models.ManyToManyField(
                through="learning.Containing", to="learning.question"
            ),
        ),
    ]
