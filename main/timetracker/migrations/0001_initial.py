# Generated by Django 5.0.6 on 2024-05-15 09:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employees',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_name', models.CharField(max_length=200)),
                ('starttime', models.TimeField()),
                ('endtime', models.TimeField()),
                ('breaktime', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Clocking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('incident', models.CharField(choices=[('CLOCK IN', 'CLOCK IN'), ('CLOCK OUT', 'CLOCK OUT')], max_length=200)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetracker.employees')),
            ],
        ),
        migrations.AddField(
            model_name='employees',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='timetracker.schedule'),
        ),
    ]