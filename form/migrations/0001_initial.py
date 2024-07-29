# Generated by Django 5.0.6 on 2024-07-28 18:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CET_Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cetPhysics', models.CharField(max_length=10)),
                ('cetChemistry', models.CharField(max_length=10)),
                ('cetMathematics', models.CharField(max_length=10)),
                ('cetPercentile', models.CharField(max_length=10)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.application')),
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
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.application')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studentname', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=15)),
                ('address', models.CharField(max_length=500)),
                ('pname', models.CharField(blank=True, max_length=100, null=True)),
                ('pnumber', models.CharField(blank=True, max_length=15, null=True)),
                ('mhMerit', models.CharField(blank=True, max_length=20, null=True)),
                ('aiMerit', models.CharField(blank=True, max_length=20, null=True)),
                ('agreed', models.BooleanField(default=False)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.application')),
            ],
        ),
        migrations.CreateModel(
            name='UploadDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applNo', models.CharField(max_length=200, null=True)),
                ('meritfile', models.FileField(upload_to='uploads/')),
                ('file_path', models.CharField(blank=True, max_length=255)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.application')),
            ],
        ),
    ]
