# Generated by Django 4.2.5 on 2023-09-23 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImageAPI', '0009_image_thumbnails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='thumbnails',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]