# Generated by Django 5.0.6 on 2024-05-15 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employees',
            name='uid',
            field=models.CharField(default='6XcdFi', max_length=10, unique=True),
        ),
    ]
