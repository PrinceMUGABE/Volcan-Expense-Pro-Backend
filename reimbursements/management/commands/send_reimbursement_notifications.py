from django.core.management.base import BaseCommand
from django.utils import timezone
from reimbursements.models import Reimbursement

class Command(BaseCommand):
    help = 'Sends notifications for unpaid reimbursements'

    def handle(self, *args, **kwargs):
        unpaid_reimbursements = Reimbursement.objects.filter(is_paid=False)
        for reimbursement in unpaid_reimbursements:
            reimbursement.check_and_notify()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {unpaid_reimbursements.count()} reimbursements'
            )
        )