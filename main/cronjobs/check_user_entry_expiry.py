from django_cron import CronJobBase, Schedule
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.template.loader import get_template
import os, json, logging, imaplib, smtplib, email, re, time
from main.models import UserEntry
from django.utils import timezone
from .base import MyCommandBase
from django.conf import settings
class Command(MyCommandBase):
    RUN_EVERY_MINS = 1 # every 2 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'check_user_entry_expiry' # a unique code

    def custom_action(self, logger):
        logger.info(f'Start {__class__.code}')
        for user_entry in UserEntry.objects.all():
            if not user_entry.to_date: # 無期限のものは無視
                pass

            elif user_entry.to_date < timezone.now().date():
                link_url = f'{settings.HOST_NAME}/queue/userentry?email={user_entry.email}&clinic={user_entry.clinic.id}'
                user_entry.notify_entry_expiry(link_url)
                user_entry.delete()
            else:
                pass
        logger.info(f'Finished {__class__.code}')
        
