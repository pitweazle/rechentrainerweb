# Generated by Django 4.0.3 on 2022-05-11 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_zaehler_optionen_alter_auswahl_bis_stufe_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='zaehler',
            name='optionen',
            field=models.ManyToManyField(null=True, to='core.auswahl'),
        ),
    ]