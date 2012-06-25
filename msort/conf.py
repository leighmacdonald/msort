from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from logging import getLogger
from os import makedirs
from os.path import expanduser, exists, dirname
from re import IGNORECASE, compile as rxcompile
class ConfigError(Exception):
    """
    Thrown on configuration issues
    """
    pass

class Config(object):
    """Simple configuration class based on RawConfigParser which will
    load the config file and create one if it doesnt exist.

    It will also parse out the regex values into proper compiled regex
    instances."""
    skip = ('general', 'ignored', 'logging', 'cleanup')

    # Static ConfigParser instance
    _config = None

    def __init__(self, config_path="~/.msort.conf", skiplist=None):
        """ Initialize the configuration. If a existing one doesnt exit a new one will be created
        in, by default, the users home directory, unless otherwise specified by the configPath
        parameter

        :param configPath: Location of the config file
        :param skip: List of filtered sections to skip when parsing for rules
        """
        self.log = getLogger(__name__)
        if not self._config:
            self._config = RawConfigParser()
            config_path = expanduser(config_path)
            self._initConfigPath(config_path)
            self._config.read(config_path)
            self._rules = self.parseRules()

    def _initConfigPath(self, config_file):
        if not exists(config_file):
            config_directory = dirname(config_file)
            try:
                if not exists(config_directory):
                    makedirs(config_directory)
                with open(config_file, 'w') as f:
                    f.write(DEFAULT_CONF_FILE)
            except (IOError, OSError) as err:
                raise ConfigError('Cannot create configuration base directory {0}'.format(config_directory))

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
                'path'   : self._config.get(section, 'path'),
                'sorted' : self._config.getboolean(section, 'sorted'),
                'rx'     : self.getSectionRegex(section)
            })
        if conf:
            self.log.debug("Loaded {0} rule sections and {1} rules.".format(
                len(conf), sum([len(r['rx']) for r in conf]))
            )
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
        if self._config.has_section(section):
            for item, value in self._rxFilter(self._config.items(section)):
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
        return filter(lambda p: p not in self.skip, self._config.sections())

    def getNextRxId(self, section, findid=1):
        """
        Return the next available free regex item key
        :param findid: Starting index
        :type findid: int
        :param section: Section to look through
        :type section: string
        :return: section regex key
        :rtype: string
        """
        while 'rx{0}'.format(findid) in [id for id, value in self._rxFilter(self._config.items(section))]:
            findid += 1
        return 'rx{0}'.format(findid)

    def getSafe(self, section, option, default=False):
        """ Get a config value providing a default value if it doesnt exist

        :param section: Config section name
        :type section: string
        :param option: Config option name
        :param default: string
        :return: config value
        :rtype: string
        """
        if self._config.has_section(section) and self._config.has_option(section, option):
            return self._config.get(section, option)
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
        if not section in self.filteredSections():
            raise ValueError('Invalid section given')
        secs = self._rxFilter(self._config.items(section))
        return secs

    @property
    def commit(self):
        return self._config.getboolean('general', 'commit')


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

[xxx]
path=XXX
sorted=false
rx1=.+?\.XXX\.
"""