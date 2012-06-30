"""
Module to scan for empty folders and directories
"""
from os.path import isdir, isfile, getsize

from msort.check import BaseCheck, CheckError
from msort.filesystem import dir_size
from msort.operation import DeleteOperation

class EmptyCheck(BaseCheck):
    def __call__(self, section, path):
        if isdir(path):
             empty = dir_size(path) == 0
        elif isfile(path):
            empty = getsize(path) == 0
        else:
            raise CheckError('Invalid file type, must be file or directory')
        if empty:
            return DeleteOperation(path)