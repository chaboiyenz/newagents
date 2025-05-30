# Generated by Django 5.2.1 on 2025-05-20 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0019_alter_subdivision_construction_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subdivision',
            name='construction_status',
            field=models.CharField(blank=True, choices=[('RFO', 'Ready For Occupancy'), ('Preselling', 'Preselling'), ('RFO/Preselling', 'RFO/Preselling')], max_length=15, null=True),
        ),
    ]
