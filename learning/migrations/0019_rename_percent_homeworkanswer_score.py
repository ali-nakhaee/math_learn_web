# Generated by Django 5.0.4 on 2024-05-10 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0018_homework_total_score"),
    ]

    operations = [
        migrations.RenameField(
            model_name="homeworkanswer",
            old_name="percent",
            new_name="score",
        ),
    ]
