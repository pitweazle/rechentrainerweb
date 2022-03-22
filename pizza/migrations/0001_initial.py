# Generated by Django 4.0 on 2022-03-21 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Pizza',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('belag1', models.CharField(max_length=100)),
                ('belag2', models.CharField(max_length=100)),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pizza.size')),
            ],
        ),
    ]
