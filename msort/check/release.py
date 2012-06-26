from msort.check import BaseCheck
from msort.conf import Config

class ReleaseCheck(BaseCheck):

    _rules = {}

    def __init__(self):
        super(ReleaseCheck, self).__init__()
        self.conf = Config()
        sections = self.conf.filteredSections()
        for section in sections:
            self._rules[section] = self.conf.getRuleList(section)
        self.log.debug(sections)

    def __call__(self, path):

        return False