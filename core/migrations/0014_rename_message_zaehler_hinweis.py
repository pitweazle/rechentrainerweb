# Generated by Django 4.0 on 2022-06-07 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_zaehler_optionen_remove_zaehler_stufe_next_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='zaehler',
            old_name='message',
            new_name='hinweis',
        ),
    ]