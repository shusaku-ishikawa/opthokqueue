from django_cron import CronJobBase
import logging
class MyCommandBase(CronJobBase):
    
    def do(self):
        logger = logging.getLogger('batch_logger')
        try:
            self.custom_action(logger)
        except Exception as e:
            logger.error(str(e))
        