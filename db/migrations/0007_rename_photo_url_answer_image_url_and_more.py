# Generated by Django 4.0.4 on 2023-06-09 23:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0006_remove_question_categories_remove_question_question_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='photo_url',
            new_name='image_url',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='photo_url',
            new_name='image_url',
        ),
    ]
