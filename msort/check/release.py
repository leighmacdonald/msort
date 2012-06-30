"""
Module help filter based on release/folder/file names
"""
import re
from os.path import basename, join

from msort.check import BaseCheck
from msort.operation import MoveOperation
from msort.transform import cleanup

class ReleaseCheck(BaseCheck):
    """
    This check will do matching against release names folders and the regex rules
    defined in the config.
    """

    _rules = {}

    def __init__(self, config):
        super(ReleaseCheck, self).__init__(config)
        for section in self.conf.filteredSections():
            rules = self.conf.getRuleList(section)
            self._rules[section] = [re.compile(pat, re.I) for _, pat in rules]

    def __call__(self, section, path):
        try:
            for pattern in self._rules[section]:
                match = pattern.search(path)
                if match:
                    try:
                        if self.conf.isSorted(section):
                            full_name = match.groupdict()['name']
                            parsed_name = cleanup(basename(full_name))
                            dest = self.conf.getDestPath(section, parsed_name)
                            return MoveOperation(path, dest)
                        else:
                            dest = self.conf.getDestPath(section)
                            if join(dest, basename(path)) == path:
                                # Make sure the final destination isnt the same as the given path
                                return False
                        return MoveOperation(path, dest)
                    except KeyError:
                        self.log.warn('Pattern matched, but no "name" group was found')
        except KeyError:
            return False