# Generated by Django 4.0 on 2022-03-21 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_remove_auswahl_ab_stufe_auswahl_bis_stufe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protokoll',
            name='wertung',
            field=models.CharField(blank=True, max_length=10, verbose_name='Wertung'),
        ),
    ]