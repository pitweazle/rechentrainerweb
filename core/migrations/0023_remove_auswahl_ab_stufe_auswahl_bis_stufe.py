# Generated by Django 4.0 on 2022-03-10 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_rename_start_jg_kategorie_start_jg_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auswahl',
            name='ab_stufe',
        ),
        migrations.AddField(
            model_name='auswahl',
            name='bis_stufe',
            field=models.IntegerField(default=0, verbose_name='bis Stufe:'),
        ),
    ]