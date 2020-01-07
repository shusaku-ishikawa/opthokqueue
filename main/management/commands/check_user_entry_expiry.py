import json
import logging
import os
from datetime import datetime, timedelta
import time
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.conf import settings
import re
import time
from main.models import *

class Command(BaseCommand):
    help = 'user_entryの期限を確認する'
    def handle(self, *args, **options):
        logger = logging.getLogger('batch_logger')
        logger.info(f'{os.path.basename(__file__)} has been started')
        for user_entry in UserEntry.objects.all():
            if not user_entry.to_date: # 無期限のものは無視
                pass
            elif user_entry.to_date < timezone.now().date():
                print(f'{user_entry} {user_entry.to_date} has been expired')
                link_url = f'{settings.HOST_NAME}/queue/userentry?email={user_entry.email}&clinic={user_entry.clinic.id}'
                user_entry.notify_entry_expiry(link_url)
                user_entry.delete()
            else:
                pass
        logger.info(f'{os.path.basename(__file__)} has been completed')

