"""
Provied capabilities related to the filesystem
"""
from collections import namedtuple
from os import statvfs, listdir as reallistdir, stat
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
        for file_name in sorted([Path(join(path, f)) for f in listdir(path)]):
            self.log.debug('Scanning file: {0}'.format(file_name))
            for checker in self._checks:
                try:
                    check_result = checker(section, file_name)
                except CheckSkip as err:
                    # Skip raised, stop checking this path and move on to the next
                    self.log.warn(err)
                    break
                except CheckError as err:
                    # Raise the error unless the general->error_continue config setting is true
                    if not self.conf.getboolean('general', 'error_continue'):
                        raise err
                    self.log.error(err)
                    continue
                else:
                    if check_result:
                        if not type(check_result) == list:
                            check_result = [check_result]
                        for result in check_result:
                            self.log.info('Check matched: {0}'.format(result))
                            found.append(result)
                        break
        return found

_ntuple_diskusage = namedtuple('usage', 'total used free')

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned value is a named tuple with attributes 'total', 'used' and
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
    return _ntuple_diskusage(total, used, free)

def fmt_size(num_bytes):
    """ Return a human readable version of the number of bytes supplied.

    :param num_bytes: Byte count
    :type num_bytes: int
    :return: Human readable size
    :rtype: str
    """
    for x in ['b','KB','MB','GB']:
        if num_bytes < 1024.0:
            return "%3.1f%s" % (num_bytes, x)
        num_bytes /= 1024.0
    return "%3.1f%s" % (num_bytes, 'TB')

def dir_size(folder):
    """ Recursively calculate the size of a path.

    This can be a directory or file

    :param folder: Path to get the size of
    :type folder: str
    :return: Total number of bytes counted
    :rtype: int
    """
    if isfile(folder): return getsize(folder)
    total_size = 0
    for item in listdir(folder):
        item_path = join(folder, item)
        if isfile(item_path):
            total_size += getsize(item_path)
        elif isdir(item_path):
            total_size += dir_size(item_path)
    return total_size

def listdir(path):
    """ Wrapper around os.listdir which returns Path objects instead of plain str's

    :param path: path to scan
    :type path: str
    :return: List of paths
    :rtype: Path[]
    """
    return (Path(p) for p in reallistdir(path)) if isdir(path) else [path]

class Path(str):
    """ Represents a filesystem path, adds a few helper properties """

    @property
    def age(self):
        """ Get the age of the path

        :return: Age in seconds
        :rtype: int
        """
        return stat(self).st_ctime

    @property
    def size(self):
        """ Get the size of the path

        :return: Path size in bytes
        :rtype: int
        """
        return dir_size(self)

    @classmethod
    def join(cls, *args):
        return Path(join(*args))



