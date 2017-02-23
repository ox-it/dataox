import datetime
import logging
import os

logger = logging.getLogger(__file__)

class _MaintenanceMode(object):
    @property
    def lock_directory(self):
        if not hasattr(self, '_lock_directory'):
            from django.conf import settings
            lock_directory = getattr(settings, 'MAINTENANCE_MODE_LOCK_DIRECTORY', None)
            if not (lock_directory and os.path.isdir(lock_directory)):
                return None
            self._lock_directory = lock_directory
        return self._lock_directory
            
    def __bool__(self):
        if not self.lock_directory:
            return False
        return any(not fn.startswith('.') for fn in os.listdir(self.lock_directory))

    def started(self):
        ctime = float('inf')
        for fn in os.listdir(self.lock_directory):
            if fn.startswith('.'):
                continue
            fn = os.path.join(self.lock_directory, fn)
            ctime = min(ctime, os.lstat(fn).st_ctime)
            #return ctime
        ctime = datetime.datetime.fromtimestamp(ctime)
        
        # If it's taken too long, raise a warning for Sentry.
        if datetime.datetime.now() - ctime > datetime.timedelta(minutes=7):
            logger.warning("We've been in maintenance mode too long")
        
        return ctime
            

MAINTENANCE_MODE = _MaintenanceMode()