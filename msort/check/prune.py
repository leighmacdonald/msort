"""
A module used to archive or remove old directories
"""
import re
from time import time
from os.path import join, isdir

from msort.filesystem import listdir, Path
from msort.operation import DeleteOperation
from msort.check import BaseCheck

DAY = 3600*24

class Pruner(BaseCheck):
    def __init__(self, config):
        super(Pruner, self).__init__(config)
        self.rules = [re.compile(pat, re.I) for _, pat in self.conf.getRuleList('prune')]
        self.ttl = self.conf.getint('prune', 'max_days') * DAY

    def __call__(self, section, path):
        if isdir(path) and self.conf.isSorted(section):
            results = []
            for sub_dir in listdir(path):
                res = self.checkAge(Path.join(path, sub_dir))
                if res:
                    results.append(res)
            return results
        else:
            return self.checkAge(path)



    def checkAge(self, path):
        age_diff = int(time() - path.age)
        if age_diff > self.ttl:
            if any([rule.match(path) for rule in self.rules]):
                return DeleteOperation(path)
        return False

