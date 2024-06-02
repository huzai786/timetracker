# Generated by Django 5.0.6 on 2024-05-21 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0008_remove_employees_id_alter_employees_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='employees',
            name='employee_flexibility',
            field=models.CharField(choices=[('Flexible', 'Flexible'), ('Strict', 'Strict')], default='Strict', max_length=100),
            preserve_default=False,
        ),
    ]
