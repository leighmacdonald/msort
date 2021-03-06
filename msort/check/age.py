"""
Module to scan for empty folders and directories
"""
from time import time

from msort.check import BaseCheck, CheckSkip

class AgeCheck(BaseCheck):
    """
    A simple checker which will validate a file or folders age.
    """
    def __call__(self, section, path):
        if self.conf.getboolean('minimum_age', 'enabled'):
            min_age = self.conf.getint('minimum_age', 'days') * 86400
            file_age = time() - path.age
            if file_age <= min_age:
                raise CheckSkip('Path does not meet minimum age requirements: {0}'.format(path))

