#!/bin/env python
"""
Author: Leigh MacDonald <leigh@cudd.li>
"""

from os import stat, listdir
from os.path import isdir, isfile

class FileSystemCleaner(object):
    def __init__(self, base_path):
        self.base_path = base_path

    def findEmptyDirectories(self, base_path=None):
        for node in listdir(base_path if base_path else self.base_path):
            print(node)

    def _getFileSize(self, file):
        return stat(file).st_size

