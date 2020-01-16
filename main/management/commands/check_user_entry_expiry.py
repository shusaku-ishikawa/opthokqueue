from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.template.loader import get_template
import os, json, logging, imaplib, smtplib, email, re, time
from main.models import UserEntry
from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        logger = logging.getLogger('batch_logger')
        logger.info('Started check_user_entry_expiry')
        for user_entry in UserEntry.objects.all():
            if not user_entry.to_date: # 無期限のものは無視
                pass

            elif user_entry.to_date < timezone.now().date():
                link_url = f'{settings.HOST_NAME}/queue/userentry?email={user_entry.email}&clinic={user_entry.clinic.id}'
                user_entry.notify_entry_expiry(link_url)
                user_entry.delete()
            else:
                pass
        logger.info('Finished check_user_entry_expiry ')
        
