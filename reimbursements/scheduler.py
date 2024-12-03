from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command

def send_reimbursement_notifications():
    call_command('send_reimbursement_notifications')

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_reimbursement_notifications, 
        trigger=CronTrigger(hour=6, minute=0),  # Runs every day at 6:00 AM
        id='send_notifications', 
        replace_existing=True
    )
    scheduler.start()
