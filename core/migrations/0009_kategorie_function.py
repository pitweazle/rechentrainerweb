# Generated by Django 4.0 on 2022-03-04 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_protokoll_options_alter_zaehler_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='kategorie',
            name='function',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
