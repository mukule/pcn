# Generated by Django 4.2.5 on 2023-09-18 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phc', '0024_county_fully_established_county_in_progress_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='county',
            name='status',
            field=models.PositiveIntegerField(default=0),
        ),
    ]