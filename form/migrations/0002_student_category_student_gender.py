# Generated by Django 5.0.6 on 2024-08-28 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='gender',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
