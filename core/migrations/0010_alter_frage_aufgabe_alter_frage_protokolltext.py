# Generated by Django 4.0 on 2022-03-04 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_kategorie_function'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frage',
            name='aufgabe',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='frage',
            name='protokolltext',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
