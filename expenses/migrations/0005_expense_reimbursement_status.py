# Generated by Django 5.0.7 on 2024-11-23 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0004_remove_expense_video_filename_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='reimbursement_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending', max_length=20),
        ),
    ]
