# Generated by Django 4.0 on 2022-06-30 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_alter_zaehler_hinweis'),
    ]

    operations = [
        migrations.AddField(
            model_name='protokoll',
            name='grafik',
            field=models.TextField(blank=True),
        ),
    ]
