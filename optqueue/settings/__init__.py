import os

k = 'queue_env'
if 'queue_env' in os.environ and os.environ['queue_env'] == 'prod':
   from .prod import *
else:
   from .dev import *
