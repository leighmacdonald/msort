"""
Provides a simple check based on lsof output to see if a path is in use by another process
"""
from time import time

from msort.log import getLogger
from msort.check import BaseCheck, CheckSkip
from msort.system import call_output

class InUseCheck(BaseCheck):
    """ Check if the file being scanned is in use """
    lsof_cache = ""
    cache_update = 0
    cache_ttl = 1

    def __init__(self, config):
        super(InUseCheck, self).__init__(config)
        self.log = getLogger(__name__)

    def __call__(self, section, path):
        t = time()
        if t - self.cache_update > self.cache_ttl:
            self.lsof_cache = call_output('lsof')
            self.cache_update = time()
        if path in self.lsof_cache:
            raise CheckSkip('Detected In-Use path, Skipping: {0}'.format(path))
        return False

