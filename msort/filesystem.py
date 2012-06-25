from collections import namedtuple
from os import statvfs, listdir, walk
from os.path import join, getsize, exists, isdir, isfile
from logging import getLogger
from msort.check import BaseCheck

class DirectoryScanner(object):
    _checks = []

    def __init__(self):
        self.log = getLogger(__name__)

    def addChecker(self, checker):
        if not isinstance(checker, BaseCheck):
            raise TypeError('Checker passed must be a instance of BaseCheck')
        if checker.__class__.__name__ in [c.__class__.__name__ for c in self._checks]:
            self.log.warn('Check already loaded, skipping: {0}'.format(checker.__class__.__name__))
        self._checks.append(checker)
        self.log.info('Added check: {0}'.format(checker.__class__.__name__))

    def find(self, path):
        found = []
        for file_name in [join(path, f) for f in listdir(path)]:
            for checker in self._checks:
                if checker(file_name):
                    found.append(file_name)
                    break
        return found

_ntuple_diskusage = namedtuple('usage', 'total used free')

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.
    """
    st = statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(fmt_size(total), fmt_size(used), fmt_size(free))

def fmt_size(num_bytes):
    for x in ('bytes','KB','MB','GB'):
        if bytes < 1024.0:
            return "%3.1f%s" % (num_bytes, x)
        num_bytes /= 1024.0
    return "%3.1f%s" % (num_bytes, 'TB')

def dir_size(folder):
    #total_size = getsize(folder) // 4096?
    total_size = 0
    for item in listdir(folder):
        itempath = join(folder, item)
        if isfile(itempath):
            total_size += getsize(itempath)
        elif isdir(itempath):
            total_size += dir_size(itempath)
    return total_size