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
    _seasons = []

    def __init__(self, config):
        super(ReleaseCheck, self).__init__(config)
        for section in self.conf.filteredSections():
            self._rules[section] = [re.compile(pat, re.I) for _, pat in self.conf.getRuleList(section)]
        if not self._seasons:
            self._seasons = [re.compile(pat, re.I) for _, pat in self.conf.getRuleList('seasons')]

    def __call__(self, section, path):
        for method in ('getSeasonMatch', 'getReleaseMatch'):
            oper = getattr(self, method)(section, path)
            if oper:
                return oper

    def getSeasonMatch(self,section, path):
        sort_seasons = self.conf.getboolean(section, 'sort_seasons', fallback=False)
        is_season = self.isSeason(path) if sort_seasons else False
        if is_season:
            raise Exception('Found season!: {0}'.format(path) )

    def getReleaseMatch(self, section, path):
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
        return False

    def isSeason(self, path):
        """ Check if the path it a season folder

        :param path:
        :type path:
        :return:
        :rtype:
        """
        match = False
        for pattern in self._seasons:
            match = pattern.search(path)
            if match:
                self.log.debug('Matched a season!')
                break
        return match

