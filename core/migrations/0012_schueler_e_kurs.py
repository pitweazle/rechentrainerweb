# Generated by Django 4.0.3 on 2022-05-19 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_rename_frage_protokoll_frage_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='schueler',
            name='e_kurs',
            field=models.BooleanField(default=True),
        ),
    ]