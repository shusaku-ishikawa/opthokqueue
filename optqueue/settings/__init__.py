import os

if 'env' in os.environ and os.environ['env'] == 'prod':
   from .prod import *
else:
   from .dev import *
