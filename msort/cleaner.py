#!/bin/env python
"""
Author: Leigh MacDonald <leigh@cudd.li>
"""

from os import stat, listdir, walk
from os.path import isdir, islink, getsize, join, exists
from shutil import rmtree
from fnmatch import fnmatch

class FileSystemCleaner(object):
    def __init__(self, base_path):
        self.base_path = base_path

    def findEmptyDirectories(self, base_path=None, min_size=1):
        """ Look for immediate (1 level) directories under the supplied base_path which contain
         empty files.

        :param base_path: Base search path
        :type base_path: str
        :param min_size: Minimum size a folder needs to be before its considered empty
        :type min_size: int
        :return: list of empty directories
        :rtype: list
        """
        delete_list = []
        base = base_path if base_path else self.base_path
        for node in listdir(base):
            full_path = join(base,node)
            if exists(full_path) and not islink(full_path) and isdir(full_path):
                size = self._getDirectorySize(full_path)
                if size < min_size:
                    print("{0:0>5}MB -> {1}".format(self.toMB(size), full_path))
                    delete_list.append(full_path)
        return delete_list

    def _getFileSize(self, file):
        """ Return the sie of a file

        :param file: File path
        :type file: str
        :return: File size in bytes
        :rtype: int
        """
        return stat(file).st_size

    def _getDirectorySize(self, directory):
        """ Calculate the size of a directory and its subdirectories

        :param directory: Directory to count
        :type directory: str
        :return: Directory total size
        :rtype: int
        """
        folder_size = 0
        try:
            for (path, dirs, files) in walk(directory):
              for file in files:
                filename = join(path, file)
                folder_size += getsize(filename)
        except OSError:
            # Make sure we don't delete something we are not sure of. This is for links mostly.
            folder_size = 1000

        return folder_size

    def _getEmptyRatio(self, directory):
        empty_files  = 0
        total_files  = 0
        for (path, dirs, files) in walk(directory):
              for file in files:
                filename = join(path, file)
                if not getsize(filename):
                    empty_files += 1
                total_files  += 1
        return empty_files, total_files

    def toMB(self, bytes):
        """ Convert bytes to megabytes

        :param bytes: Size in bytes
        :type bytes: int
        :return: Size in MB
        :rtype: int
        """
        return int(bytes / (1024.0 * 1024.0))

    def wipePattern(self, file_path, patterns=('*.m3u', '*.pls', '*')):
        # This is clearly wrong, just commiting to sync
        return any(map(fnmatch(file_path, patterns)))

    def wipeDirs(self, directories, raise_on_fail=False):
        """ Attempt to remove the directory tree from the filesystem permanently

        :param directories: Directories to delete
        :type directories: str[]
        :param raise_on_fail: Should failure to delete be ignored?
        :type raise_on_fail: bool
        :return: number of successful and failed executions
        :rtype: int, int
        """
        failed  = 0
        success = 0
        for d in directories:
            try:
                rmtree(d)
                success += 1
            except Exception as err:
                if raise_on_fail: raise err
                failed += 1
        return success, failed

    def findCorruptDirectories(self, base_path=None, zero_limit=1):
        """ Find directories with any 0 byte files inside

        :param base_path:
        :type base_path:
        :param zero_limit:
        :type zero_limit:
        :return:
        :rtype:
        """
        corrupt = []
        base = base_path if base_path else self.base_path
        for node in listdir(base):
            full_path = join(base,node)
            if exists(full_path) and not islink(full_path) and isdir(full_path):
                ratio = self._getEmptyRatio(full_path)
                corrupt.append((full_path, ratio))
        return corrupt

