""" Confiuguration module """
try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser, NoOptionError, NoSectionError
from os.path import expanduser, join, exists
from re import IGNORECASE, compile as rxcompile

from msort.log import getLogger

class ConfigError(Exception):
    """
    Thrown on configuration issues
    """
    pass

class Config(ConfigParser):
    """Simple configuration class based on RawConfigParser which will
    load the config file and create one if it doesnt exist.

    It will also parse out the regex values into proper compiled regex
    instances."""
    skip = ('general', 'ignored', 'logging', 'cleanup')

    def __init__(self, config_path="~/.msort.conf"):
        """ Initialize the configuration. If a existing one doesnt exit a new one will be created
        in, by default, the users home directory, unless otherwise specified by the configPath
        parameter

        :param config_path: Location of the config file
        :type config_path: str
        """
        ConfigParser.__init__(self)
        self.log = getLogger(__name__)
        config_path = expanduser(config_path)
        if not exists(config_path):
            raise ConfigError('Invalid config file, doesnt exist: {0}'.format(config_path))
        self.log.debug('Reading config: {0}'.format(config_path))
        self.read(config_path)
        self._rules = self.parseRules()

    def getRules(self):
        """Return the loaded ruleset

        :return: List of rules loaded
        :rtype: list
        """
        return self._rules

    def parseRules(self):
        """ Parse the raw configuration options into nicely formatted
        dict's for simple usage.

        :return: list of option dicts
        :rtype: list
        """
        conf = list()
        for section in self.filteredSections():
            conf.append({
                'name'   : section,
                'source' : self.get(section, 'source'),
                'dest'   : self.get(section, 'dest'),
                'sorted' : self.getboolean(section, 'sorted'),
                'rx'     : self.getSectionRegex(section)
            })
        if conf:
            self.log.debug("Loaded {0} rule sections and {1} rules.".format(len(conf), sum([len(r['rx']) for r in conf])))
        return conf

    def getSectionRegex(self, section):
        """ Build and return a list of the regex fields for the section
        provided. All fields starting with 'rx' are considered valid regex
        rules to attempt to use.

        :param section: Config file section name
        :type section: string
        :return: List of regular expressions
        :rtype: list
        """
        regexList = []
        if self.has_section(section):
            for item, value in self._rxFilter(self.items(section)):
                regexList.append(rxcompile(value, IGNORECASE))
        return regexList

    def _rxFilter(self, iter):
        """ Filter to only regex items

        :param iter: Regex configuration tuples
        :type iter: list
        :return:
        """
        return filter(lambda i: i[0].startswith('rx'), iter)

    def filteredSections(self):
        """ Get a list of valid ruleset sections

        :return: Filtered sections
        :rtype: check
        """
        return filter(lambda s: s in self.get('general', 'scan_sections').split(',')
            and self.sectionEnabled(s), self.sections())

    def sectionEnabled(self, section):
        """ Fetch and return the "enabled" status of the supplied section.

        :param section: Section Key
        :type section: str
        :return: Enabled status
        :rtype: bool
        """
        try:
            return self.getboolean(section, 'enabled')
        except Exception as err:
            return True

    def getNextRxId(self, section, find_id=1):
        """
        Return the next available free regex item key
        :param find_id: Starting index
        :type find_id: int
        :param section: Section to look through
        :type section: string
        :return: section regex key
        :rtype: string
        """
        while 'rx{0}'.format(find_id) in [id for id, _ in self._rxFilter(self.items(section))]: find_id += 1
        return 'rx{0}'.format(find_id)

    def getSafe(self, section, option, default=False):
        """ Get a config value providing a default value if it doesnt exist

        :param section: Config section name
        :type section: string
        :param option: Config option name
        :param default: string
        :return: config value
        :rtype: string
        """
        if self.has_section(section) and self.has_option(section, option):
            return self.get(section, option)
        return default

    def addRule(self, section, rule):
        """ Add a new regex rule to the configuration of a given section

        :param section: configuration section
        :type section: str
        :param rule: Regex pattern
        :type rule: str
        :return: Add status
        :rtype: bool

        """
        pass

    def getRuleList(self, section):
        return self._rxFilter(self.items(section))

    def getSourcePath(self, section):
        return self.get(section, 'source')

    def getDestPath(self, section, filename=None):
        return join(self.get(section, 'dest'), filename if filename else '')

    def isSorted(self, section, default=False):
        try:
            return self.getboolean(section, 'sorted')
        except Exception:
            return default

DEFAULT_CONF_FILE = """[general]
basepath = /mnt/storage
commit = true
lock_enabled = true
lock_pattern = ^\.(incomplete|lock|locked)
new_pattern  = ^(.+?\.){2,}.+?-(.*)$
error_continue=false

[cleanup]
enable = true
delete_empty = true
rx1=(\.avi|\.mkv)$

[logging]
enabled=true
# NOTSET = 0 | DEBUG = 10 | INFO = 20 | WARN = 30 | ERROR = 40 | FATAL = 50
level=10
format="%(levelname)s %(message)s"

[ignored]
rx1=(.avi|.mkv)$
rx2=(.txt|.nfo)$

[tv]
source = /mnt/storage/TV
dest=/mnt/storage/TV
sorted=true
rx1=(?P<name>.+?).S\d{1,2}E\d{1,2}
rx2=(?P<name>.+?).\d{1,2}X\d{2}

[xvid]
source = /mnt/storage/XVID
dest=/mnt/storage/XVID
sorted=false
rx1=(?P<name>^.+?[12]\d{3}).+?(dvd|bd)rip.+?Xvid

[dvdr]
source = /mnt/storage/XVID
dest = /mnt/storage/DVDR
sorted=false
rx1=.+?(PAL|NTSC).DVDR
"""