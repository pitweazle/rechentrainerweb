# Generated by Django 4.0 on 2022-07-10 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_alter_protokoll_eingabe_alter_protokoll_kategorie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='protokoll',
            name='individuell',
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
    ]