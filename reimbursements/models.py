from django.db import models
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from expenses.models import Expense

class Reimbursement(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name="reimbursement")
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_notification_sent = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # If is_paid is being set to True, update the corresponding expense's status to 'paid'
        if self.is_paid and not self.paid_at:
            self.paid_at = now()  # Set the paid_at timestamp to the current time
            self.expense.status = 'paid'  # Update the status of the associated expense
            self.expense.save()

        # Skip notifications during creation to avoid primary key errors
        if not self.pk:  # If object has no primary key, it is being created
            super().save(*args, **kwargs)
            return

        # Check if notification should be sent (if it's been 24 hours since last notification)
        if not self.is_paid and (
            not self.last_notification_sent or 
            now() - self.last_notification_sent > timedelta(days=1)
        ):
            self.check_and_notify()
            self.last_notification_sent = now()

        super().save(*args, **kwargs)

    def check_and_notify(self):
        if not self.is_paid:
            driver = self.expense.user
            manager = driver.created_by  # Assuming you have a 'created_by' field in your User model
            admin = manager.created_by if manager else None

            # Email to the driver
            send_mail(
                subject="Pending Reimbursement Notification",
                message=(
                    f"Hello {driver.phone_number},\n"
                    f"Your expense for {self.expense.category} logged on {self.expense.date} "
                    "has been approved but not yet reimbursed. Please remind your manager to follow up."
                ),
                from_email="no-reply@expensepro.com",
                recipient_list=[driver.email],
            )

            # Email to the manager
            if manager:
                send_mail(
                    subject="Driver Expenses Pending Reimbursement",
                    message=(
                        f"Hello {manager.phone_number},\n"
                        f"The following expense for a driver under your supervision is pending reimbursement:\n"
                        f" - Driver: {driver.phone_number}, Expense: {self.expense.category}, "
                        f"Date: {self.expense.date}\n"
                        "Please follow up with the admin."
                    ),
                    from_email="no-reply@expensepro.com",
                    recipient_list=[manager.email],
                )

            # Email to the admin
            if admin:
                send_mail(
                    subject="Pending Reimbursements for Drivers",
                    message=(
                        f"Hello {admin.phone_number},\n"
                        f"Expenses for drivers under {manager.phone_number} remain unpaid. "
                        "Kindly process these reimbursements promptly."
                    ),
                    from_email="no-reply@expensepro.com",
                    recipient_list=[admin.email],
                )
