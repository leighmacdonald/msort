from msort.check import BaseCheck
from msort.conf import Config

class ReleaseCheck(BaseCheck):
    def __init__(self):
        self.conf = Config()

    def __call__(self, path):
        print self.conf.getRules()
        return False