# Generated by Django 4.0 on 2022-03-04 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_frage_aufgabe_alter_frage_protokolltext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frage',
            name='aufgabe',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AlterField(
            model_name='frage',
            name='protokolltext',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
