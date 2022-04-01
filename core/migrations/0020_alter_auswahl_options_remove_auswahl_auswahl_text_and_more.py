# Generated by Django 4.0 on 2022-03-10 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auswahl'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auswahl',
            options={'verbose_name': 'Auswahl', 'verbose_name_plural': 'Auswahl'},
        ),
        migrations.RemoveField(
            model_name='auswahl',
            name='auswahl_text',
        ),
        migrations.AddField(
            model_name='auswahl',
            name='text',
            field=models.CharField(default=0, max_length=80, verbose_name='Text'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auswahl',
            name='ab_stufe',
            field=models.IntegerField(default=0, verbose_name='ab Stufe:'),
        ),
    ]