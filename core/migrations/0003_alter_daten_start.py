# Generated by Django 4.0 on 2022-02-25 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_zusatz_daten_zaehler_zusatz_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daten',
            name='start',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Start'),
        ),
    ]