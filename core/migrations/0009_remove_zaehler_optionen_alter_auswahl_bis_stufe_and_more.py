# Generated by Django 4.0.3 on 2022-05-07 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_zaehler_optionen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zaehler',
            name='optionen',
        ),
        migrations.AlterField(
            model_name='auswahl',
            name='bis_stufe',
            field=models.IntegerField(default=0, verbose_name='bis Stufe (ex):'),
        ),
        migrations.AlterField(
            model_name='auswahl',
            name='kategorie',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.kategorie'),
        ),
    ]
