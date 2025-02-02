# Generated by Django 5.0.7 on 2024-11-23 14:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('expenses', '0005_expense_reimbursement_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reimbursement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expense', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reimbursement', to='expenses.expense')),
            ],
        ),
    ]
