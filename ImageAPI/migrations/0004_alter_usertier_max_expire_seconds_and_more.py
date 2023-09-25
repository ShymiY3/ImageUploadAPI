# Generated by Django 4.2.5 on 2023-09-23 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImageAPI', '0003_usertier_max_expire_seconds_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertier',
            name='max_expire_seconds',
            field=models.PositiveIntegerField(blank=True, default=30000, null=True),
        ),
        migrations.AlterField(
            model_name='usertier',
            name='min_expire_seconds',
            field=models.PositiveIntegerField(blank=True, default=300, null=True),
        ),
        migrations.AlterField(
            model_name='usertier',
            name='thumbnail_sizes',
            field=models.JSONField(default=[200]),
        ),
    ]