# Generated by Django 5.2.1 on 2025-05-22 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0021_alter_subdivision_construction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='reset_token_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
