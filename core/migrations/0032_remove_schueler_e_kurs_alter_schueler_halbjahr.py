# Generated by Django 4.0 on 2022-07-10 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_protokoll_anmerkung_alter_protokoll_pro_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schueler',
            name='e_kurs',
        ),
        migrations.AlterField(
            model_name='schueler',
            name='halbjahr',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
