from collections import namedtuple
from os import statvfs, listdir
from os.path import join, getsize, isdir, isfile
from msort.log import getLogger
from msort.check import BaseCheck, CheckError, CheckSkip

class DirectoryScanner(object):
    """
    High-Level Class used to scan and check paths using the registered checkers
    """
    def __init__(self, config):
        self.log = getLogger(__name__)
        self._checks = []
        self.conf = config

    def registerChecker(self, checker):
        """ Register a new checker instance to be used when scanning directories.

        :param checker: A checker instance to register
        :type checker: BaseCheck
        :raises: TypeError
        """
        if not isinstance(checker, BaseCheck):
            raise TypeError('Checker passed must be a instance of BaseCheck')
        if checker.__class__.__name__ in [c.__class__.__name__ for c in self._checks]:
            self.log.warn('Check already loaded, skipping: {0}'.format(checker.__class__.__name__))
        self._checks.append(checker)
        self.log.info('Registered check instance: {0}'.format(checker.__class__.__name__))

    def find(self, section):
        """ Scan the source directory of the supplied section. For each node found
        run each of the registered checker instances against it. When a checker matches
        it will return a BaseOperation instance which when called will take the required
        steps that the check deemed required.

        :param section: Section name to get the scan directory from
        :type section: str
        :return: list of BaseOperations to be executed upon users discretion
        :rtype: list
        """
        path = self.conf.getSourcePath(section)
        found = []
        self.log.warn('Starting scan of section {0}: {1}'.format(section, path))
        for file_name in sorted([join(path, f) for f in listdir(path)]):
            self.log.debug('Scanning file: {0}'.format(file_name))
            for checker in self._checks:
                try:
                    check_result = checker(section, file_name)
                except CheckSkip as err:
                    self.log.warn(err)
                    continue
                except CheckError as err:
                    if not self.conf.getboolean('general', 'error_continue'):
                        raise err
                    self.log.error(err)
                else:
                    if check_result:
                        self.log.info('Check matched: {0}'.format(check_result))
                        found.append(check_result)
                        break
        return found

_ntuple_diskusage = namedtuple('usage', 'total used free')

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.

    :param path: Path to get stats for
    :type path: str
    :returns: Names tuple
    :type: namedtuple
    """
    st = statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(fmt_size(total), fmt_size(used), fmt_size(free))

def fmt_size(num_bytes):
    """ Return a human readable version of the number of bytes supplied.

    :param num_bytes: Byte count
    :type num_bytes: int
    :return: Human readable size
    :rtype: str
    """
    for x in ('bytes','KB','MB','GB'):
        if bytes < 1024.0:
            return "%3.1f%s" % (num_bytes, x)
        num_bytes /= 1024.0
    return "%3.1f%s" % (num_bytes, 'TB')

def dir_size(folder):
    """ Recursivly calculate the size of a directory

    :param folder: Path to get the size of
    :type folder: str
    :return: Total number of bytes counted
    :rtype: int
    """
    #total_size = getsize(folder) // 4096?
    total_size = 0
    for item in listdir(folder):
        itempath = join(folder, item)
        if isfile(itempath):
            total_size += getsize(itempath)
        elif isdir(itempath):
            total_size += dir_size(itempath)
    return total_size



