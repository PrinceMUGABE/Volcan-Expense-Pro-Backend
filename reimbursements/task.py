from celery import shared_task
from django.utils.timezone import now
from .models import Reimbursement

@shared_task
def send_reimbursement_notifications():
    """
    Task to send notifications for all unpaid reimbursements.
    This will be scheduled to run daily at 6:00 AM.
    """
    unpaid_reimbursements = Reimbursement.objects.filter(is_paid=False)
    for reimbursement in unpaid_reimbursements:
        reimbursement.check_and_notify()
    return f"Processed {len(unpaid_reimbursements)} unpaid reimbursements"