# Generated by Django 5.0.6 on 2024-07-22 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0004_alter_uploaddoc_applno'),
    ]

    operations = [
        migrations.CreateModel(
            name='CET_Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cetPhysics', models.CharField(max_length=10)),
                ('cetChemistry', models.CharField(max_length=10)),
                ('cetMathematics', models.CharField(max_length=10)),
                ('cetPercentile', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='JEE_Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jeePhysics', models.CharField(max_length=10)),
                ('jeeChemistry', models.CharField(max_length=10)),
                ('jeeMathematics', models.CharField(max_length=10)),
                ('jeePercentile', models.CharField(max_length=10)),
            ],
        ),
        migrations.DeleteModel(
            name='Exam',
        ),
    ]
