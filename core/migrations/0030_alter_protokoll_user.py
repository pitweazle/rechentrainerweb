# Generated by Django 4.0.3 on 2022-04-04 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_remove_protokoll_typ_zaehler_typ_anf_zaehler_typ_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protokoll',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protokoll', to='core.frage', verbose_name='User'),
        ),
    ]
