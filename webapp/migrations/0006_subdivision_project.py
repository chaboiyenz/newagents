# Generated by Django 5.2 on 2025-04-19 20:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_remove_subdivision_city_delete_project_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subdivision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, default='subdivisions/default.jpg', upload_to='subdivisions/')),
                ('description', models.TextField(blank=True)),
                ('price_min', models.DecimalField(decimal_places=2, help_text='Minimum price in PHP', max_digits=12)),
                ('price_max', models.DecimalField(decimal_places=2, help_text='Maximum price in PHP', max_digits=12)),
                ('messenger_link', models.URLField(blank=True, help_text='Optional Facebook Messenger link', max_length=255, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdivisions', to='webapp.city')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subdivision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='webapp.subdivision')),
            ],
        ),
    ]
