# Generated by Django 5.1.7 on 2025-05-13 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0015_alter_memo_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='subdivision',
            name='construction_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='subdivision',
            name='developer',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='subdivision',
            name='google_drive_link',
            field=models.URLField(blank=True, help_text='Optional Google Drive link', max_length=255, null=True),
        ),
    ]
