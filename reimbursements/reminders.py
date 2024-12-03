from django.core.mail import send_mail
from django.utils.timezone import now

def send_reimbursement_reminders():
    from expenses.models import Expense  # Lazy import here to avoid circular dependency
    today = now().date()

    # Fetch all approved expenses not yet reimbursed
    pending_expenses = Expense.objects.filter(
        status='approved', reimbursement_status='pending'
    )

    for expense in pending_expenses:
        driver = expense.user
        manager = driver.created_by  # Who added the driver
        admin = manager.created_by if manager else None  # Who added the manager

        # Send email to the driver
        send_mail(
            subject="Pending Reimbursement",
            message=(f"Hello {driver.phone_number},\n"
                     f"Your expense for {expense.category} logged on {expense.date} "
                     "has been approved but not yet reimbursed. "
                     "Please remind your manager to follow up.\n"),
            from_email="no-reply@expensepro.com",
            recipient_list=[driver.email],
        )

        # Send email to the manager
        if manager:
            send_mail(
                subject="Driver Expenses Pending Reimbursement",
                message=(f"Hello {manager.phone_number},\n"
                         f"The following expenses for drivers under your supervision are pending reimbursement:\n"
                         f" - Driver: {driver.phone_number}, Expense: {expense.category}, Date: {expense.date}\n"
                         "Please follow up with the admin.\n"),
                from_email="no-reply@expensepro.com",
                recipient_list=[manager.email],
            )

        # Send email to the admin
        if admin:
            send_mail(
                subject="Pending Reimbursements for Drivers",
                message=(f"Hello {admin.phone_number},\n"
                         f"Expenses for drivers under {manager.phone_number} remain unpaid. "
                         "Kindly process these reimbursements promptly.\n"),
                from_email="no-reply@expensepro.com",
                recipient_list=[admin.email],
            )
