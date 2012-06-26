from os.path import isdir, isfile, getsize
from msort import MSortError
from msort.check import BaseCheck
from msort.filesystem import dir_size
from msort.operation import DeleteOperation

class EmptyCheck(BaseCheck):
    def __call__(self, section, path):
        if isdir(path):
             empty = dir_size(path) == 0
        elif isfile(path):
            empty = getsize(path) == 0
        else:
            raise MSortError('Invalid file type, must be file or directory')
        if empty:
            return DeleteOperation(path)