#!/bin/env python
"""
Author: Leigh MacDonald <leigh@cudd.li>
"""

from os import stat, listdir, walk
from os.path import isdir, islink, getsize, join, exists
from shutil import rmtree

class FileSystemCleaner(object):
    def __init__(self, base_path):
        self.base_path = base_path

    def findEmptyDirectories(self, base_path=None, min_size=1):
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
        return stat(file).st_size

    def _getDirectorySize(self, directory):
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

    def toMB(self, bytes):
        return int(bytes / (1024.0 * 1024.0))

    def wipeDirs(self, directories):
        failed  = 0
        success = 0
        for d in directories:
            try:
                rmtree(d)
                success += 1
            except Exception:
                failed += 1
        return success, failed