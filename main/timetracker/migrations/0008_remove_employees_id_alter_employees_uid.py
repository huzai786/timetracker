# Generated by Django 5.0.6 on 2024-05-18 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0007_employees_created_alter_employees_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employees',
            name='id',
        ),
        migrations.AlterField(
            model_name='employees',
            name='uid',
            field=models.IntegerField(primary_key=True, serialize=False, unique=True),
        ),
    ]
