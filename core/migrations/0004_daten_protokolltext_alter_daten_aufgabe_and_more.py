# Generated by Django 4.0.1 on 2022-02-19 13:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_result_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='daten',
            name='protokolltext',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='daten',
            name='aufgabe',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='daten',
            name='text',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='frage',
            name='text',
            field=models.CharField(blank=True, default='Berechne:', max_length=40),
        ),
        migrations.AlterField(
            model_name='schueler',
            name='jahrgang',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterField(
            model_name='schueler',
            name='voreinst',
            field=models.IntegerField(default=1, editable=False),
        ),
    ]
