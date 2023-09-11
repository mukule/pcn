# Generated by Django 4.2.5 on 2023-09-11 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phc', '0009_questionnaire_step'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionnaire',
            name='Step',
        ),
        migrations.AddField(
            model_name='question',
            name='Step',
            field=models.CharField(blank=True, choices=[('step1', 'Governance and coordination- co-created PCN implementation with County government, MoH, Partners, and other stakeholders'), ('step2', 'Conduct a baseline survey to identify PHC needs:'), ('step3', 'Disseminating of the baseline report to the CHMT and using it to set PHC improvement indicators:'), ('step4', 'Is there support to the PCN in the following aspects:')], max_length=10, null=True),
        ),
    ]
