# Generated by Django 4.0 on 2022-07-10 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_protokoll_individuell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protokoll',
            name='anmerkung',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='protokoll',
            name='pro_text',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
