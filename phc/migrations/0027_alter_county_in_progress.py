# Generated by Django 4.2.5 on 2023-09-21 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phc', '0026_county_styleid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='county',
            name='in_progress',
            field=models.FloatField(default=0.0, verbose_name='In Progress (%)'),
        ),
    ]
