from django.conf import settings
from django.db import models



class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('fuel', 'Fuel'),
        ('toll', 'Toll'),
        ('parking', 'Parking'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the user who logged the expense
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)  # Expense category
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Expense amount
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)  # Optional receipt image
    video = models.FileField(upload_to='expense_videos/', blank=True, null=True)  # Video evidence
    date = models.DateField(blank=True, null=True)  # Expense date (parsed from receipt, if available)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Approval status
    vendor = models.CharField(max_length=200, blank=True, null=True)
    
    reimbursement_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('rejected', 'Rejected')],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)  # When the expense was logged

    def __str__(self):
        return f"{self.user.id} - {self.category} - {self.amount} ({self.status})"
