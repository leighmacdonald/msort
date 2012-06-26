import re
from os.path import basename, join
from msort.check import BaseCheck
from msort.operation import MoveOperation

class ReleaseCheck(BaseCheck):

    _rules = {}

    def __init__(self, config):
        super(ReleaseCheck, self).__init__(config)

        sections = self.conf.filteredSections()
        for section in sections:
            rules = self.conf.getRuleList(section)
            self._rules[section] = [re.compile(pat, re.I) for _, pat in rules]
        self.log.debug(sections)

    def __call__(self, section, path):
        try:
            for pattern in self._rules[section]:
                match = pattern.search(path)
                if match:
                    try:
                        if self.conf.isSorted(section):
                            full_name = match.groupdict()['name']
                            parsed_name = basename(full_name)
                            dest = self.conf.getDestPath(section, parsed_name)
                            return MoveOperation(path, dest)
                        else:
                            dest = self.conf.getDestPath(section)
                        return MoveOperation(path, dest)
                    except KeyError:
                        self.log.warn('Pattern matched, but no "name" group was found')
        except KeyError:
            return False