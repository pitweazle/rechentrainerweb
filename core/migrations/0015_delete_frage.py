# Generated by Django 4.0 on 2022-06-07 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_rename_message_zaehler_hinweis'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Frage',
        ),
    ]