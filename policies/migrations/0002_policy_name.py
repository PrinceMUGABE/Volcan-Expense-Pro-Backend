# Generated by Django 4.2.17 on 2024-12-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
