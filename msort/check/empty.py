from os.path import isdir, isfile, getsize
from msort.check import BaseCheck
from msort.filesystem import dir_size

class EmptyCheck(BaseCheck):
    def __call__(self, section, path):
        if isdir(path):
            return dir_size(path) == 0
        elif isfile(path):
            return getsize(path) == 0
