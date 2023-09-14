# Generated by Django 4.2.5 on 2023-09-14 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phc', '0020_alter_subcounty_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcounty',
            name='status',
            field=models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Process'), ('Fully Established', 'Fully Established')], default='not_started', max_length=20),
        ),
    ]
