# Generated by Django 5.0.4 on 2024-05-20 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0023_alter_homework_publish_date_end_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="homeworkanswer",
            old_name="score",
            new_name="raw_score",
        ),
    ]