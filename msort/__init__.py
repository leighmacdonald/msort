from re import compile as rxcompile, IGNORECASE
from sys import exit
from os import listdir, mkdir, walk, sep, readlink, access, EX_OK, remove, stat, rmdir
from os.path import exists, join, normpath, abspath, expanduser, isdir, isfile, getsize, basename
from shutil import rmtree
try:
    from configparser import RawConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from shutil import move
from logging import getLogger, Formatter, StreamHandler, INFO, basicConfig

def friendlysize(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in walk(start_path):
        total_size += sum([getsize(join(dirpath, f)) for f in filenames])
    return total_size

def logInit(config=None):
    """Initialize the logger class
    :param config: Config instance
    :type config: Config
    :return: logger instance
    :rtype: RootLogger
    """
    global log

    log = getLogger(__name__)
    if config and config.has_section('logging'):
        # Make a global logging object.
        level = int(config.getSafe('logging', 'level', INFO))
        log.setLevel(level)
        h = StreamHandler()
        #f = Formatter("%(levelname)s %(message)s")
        f = Formatter("%(message)s")
        h.setFormatter(f)
        log.addHandler(h)
    else:
        log.setLevel(INFO)
    return log
log = logInit()

class ChangeSet:
    """ A simple changeset to be executed """
    def __init__(self, src, dst=None, operation=move):
        """
        :param src: Source file/dir
        :type src: Location
        :param dst: Destination file/dir
        :type dst: Location
        """
        self.source = src
        self.dest = dst
        if not hasattr(operation, '__call__'):
            raise AttributeError('Operation must be callable')
        self.oper = operation
        self.log = getLogger(__name__)

    @classmethod
    def remove(cls, path):
        """ Return a changeset to remove the given file or path from the filesystem

        :param cls: ChangeSet
        :type cls: ChangeSet
        :param path:
        :type path: Location
        :return: Changeset instance to be executed
        :rtype: ChangeSet
        """
        if not exists(path):
            raise OSError('Invalid path: {0}'.format(path))
        if isdir(path):
            o = rmtree
        elif isfile(path):
            o = remove
        return cls(path, operation=o)

    def __call__(self, *args, **kwargs):
        """ Execute the operation under the operation property

        :param commit: Actually run the operation?
        :type commit: bool
        """
        commit = kwargs['commit'] if 'commit' in kwargs else False
        if commit:
            self.log.info(self)
            if self.dest:
                return self.oper(self.source, self.dest)
            else:
                return self.oper(self.source)
        else:
            self.log.info(self)
            
    def __str__(self):
        """ Show a simple string example of the operation to be performed

        :return: shell like representation of the operation
        :rtype: str
        """
        return '{2} {0} {1}'.format(self.source, self.dest if self.dest else '', self.oper.__name__)

class ConfigError(Exception):
    """
    Thrown on configuration issues
    """
    pass

class Config(RawConfigParser):
    """Simple configuration class based on RawConfigParser which will
    load the config file and create one if it doesnt exist.

    It will also parse out the regex values into proper compiled regex
    instances."""
    _DEFAULT = """[general]
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
path=TV
sorted=true
rx1=(?P<name>.+?).S\d{1,2}E\d{1,2}
rx2=(?P<name>.+?).\d{1,2}X\d{2}

[xvid]
path=XVID
sorted=false
rx1=(?P<name>^.+?[12]\d{3}).+?(dvd|bd)rip.+?Xvid

[dvdr]
path=DVDR
sorted=false
rx1=.+?(PAL|NTSC).DVDR

[xxx]
path=XXX
sorted=false
rx1=.+?\.XXX\.
"""
    skip = ('general', 'ignored', 'logging', 'cleanup')

    def __init__(self, configPath="~/.msort.conf", skiplist=None):
        """ Initialize the configuration. If a existing one doesnt exit a new one will be created
        in, by default, the users home directory, unless otherwise specified by the configPath
        parameter

        :param configPath: Location of the config file
        :param skip: List of filtered sections to skip when parsing for rules
        """
        RawConfigParser.__init__(self)
        self.log = getLogger(__name__)
        if skiplist:
            self.skip = skiplist
        self.confPath = expanduser(configPath)
        self._initConfigPath()
        self.read(self.confPath)
        self._rules = self.parseRules()

    def _initConfigPath(self):
        if not exists(self.confPath):
            try:
                pcs = self.confPath.split(sep)
                dirPath = pcs[:-1]
                p = sep
                for path in dirPath:
                    p = join(p, path)
                mkdirp(p)
                with open(self.confPath, 'w') as f:
                    f.write(self._DEFAULT)
            except IOError as err:
                raise ConfigError(err.strerror)
            except OSError:
                raise ConfigError('Cannot create configuration base directory {0}'.format(p))
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
                'path'   : self.get(section, 'path'),
                'sorted' : self.getboolean(section, 'sorted'),
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
        :rtype: filter
        """
        return filter(lambda p: p not in self.skip, self.sections())

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
        while 'rx{0}'.format(findid) in [id for id, value in self._rxFilter(self.items(section))]:
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
        if not section in self.filteredSections():
            raise ValueError('Invalid section given')
        secs = self._rxFilter(self.items(section))
        return secs

    @property
    def commit(self):
        return self.getboolean('general', 'commit')


class Location:
    """ Define a location to use, optionally validating it on
    instantiation """
    def __init__(self, *args, **kwargs):
        """ Initialize and optionally validate the path given
        
        :param paths: N number of paramerters to be joined into a complete path
        :type paths: string
        :param validate: Check the exitence of the path
        :type validate: bool
        """
        path = ''
        for p in args:
            if hasattr(p, 'path'):
                path = join(path, p.path)
            else:
                path = join(path, p)
        self._path = path

    @property
    def size(self):
        return get_size(self.path)

    @property
    def path(self):
        """ Get the current path specified

        :return: Given path
        :rtype: string
        """
        return self._path

    @property
    def basename(self):
        return basename(self.path)

    def exists(self):
        """ Check if the current location exists
        :return: Existence status
        :rtype: bool
        """
        return exists(self._path)

    def __str__(self):
        """
        Return the current path as a string representation
        """
        return self.path

class MSorter:
    """
    Media sorting class
    """
    def __init__(self, location=None, config=None):
        """ Initialize the base path and the configuration values

        :param location: Base sort path to look through
        :type location: Location
        :param config: Config instance
        :type: Config
        """
        if config:
            self.config = config
        else:
            self.config = Config()
        self.log = getLogger(__name__)

        if location:
            self.setBasePath(location)
        else:
            if self.config.has_option('general', 'basepath'):
                self.setBasePath(Location(self.config.get('general', 'basepath'), validate=True))
            else:
                raise ConfigError('"basepath" must be defined in [general] ({0})'.format(self.config.confPath))
        self.rules = self.config.getRules()
        if not self.rules:
            raise ConfigError("You must define at least 1 ruleset in the config. ({0})".format(self.config.confPath))
        if not self.config.has_option('general', 'new_pattern'):
            raise ConfigError('"new_pattern" must be defined in [general] ({0})'.format(self.config.confPath))
        self.newPattern = rxcompile(self.config.get('general', 'new_pattern'))
        if self.config.has_section('ignored'):
            self.ignores = self.config.getSectionRegex('ignored')
            self.log.debug('Loaded {0} ignore patterns.'.format(len(self.ignores)))
        else:
            self.log.warn('No ignore patterns defined')

            
    def setBasePath(self, path):
        """ Sets the base media path everything is relative to

        :param path: Base path used for searching
        :type path: Location
        """
        self.basePath = path
        self.log.debug("Set base path to: {0}".format(path))

    def genFileList(self, path=''):
        """
        Generate a list of files to scan through

        :return: File list for base directory
        :rtype: list
        """
        src = path if path else self.basePath
        dirs = listdir(src)
        file_list = []
        for d in dirs:
            file_list.append(Location(join(src, d)))
        return file_list

    def filterIgnored(self, paths):
        """ Remove any ignored files from the given list of files

        :param paths: List of files to check
        :type paths: list
        :return: List of validated files
        :rtype: list
        """
        def isok(p):
            return not any([rx.search(p.path) for rx in self.ignores])
        return filter(isok, paths)
    
    def isNew(self, file):
        """ Do a "new check" on the given file. Currently just looks for "SNNENN"
        
        :param file: File to check
        :type file: Location
        :return: New status
        :rtype: bool
        """
        return bool(self.newPattern.search(file.path))

    def findCleanupFiles(self, path):
        """
        Find files to delete from disk
        
        :param path:
        :param filelist:
        :return: Deleteable files
        :rtype: list
        """
        filelist = []
        rxlist = self.config.getSectionRegex('cleanup')
        for f in self.genFileList(path):
            for rx in rxlist:
                if isfile(f):
                    if rx.search(f):
                        filelist.append(f)
                        continue
                elif isdir(f):
                    if self.dirIsEmpty(f) and get_size(f) == 0:
                        filelist.append(f)
                        continue
        return list(set(filelist))

    def dirIsEmpty(self, path):
        """ Check for a directory's empty-ness

        :param path: Full path to a directory to check
        :type path: str
        :return: empty status
        :rtype: bool
        """
        return bool(not listdir(path)) or not path.size

    def findNew(self, releases):
        """ Find any files that look "new", this means unsorted, not
        necessarily new files.
        
        :param releases: list of directories to look through
        :type releases: list filter
        :return: New files
        :rtype: filter
        """
        new = []
        for directory in releases:
            if self.isNew(directory):
                new.append(directory)
        return new

    def _genPath(self, filename):
        """ Generate a path from the basepath

        :param filename: File name
        :type filename: str
        :return: Full path to filename
        :rtype: str
        """
        return "{0}/{1}".format(self.basePath, filename)

    def findParentDir(self, path, dest=None, mtype=None):
        """ Find the parent path of the media folder supplied

        :param path: Base path to search from
        :type path: Location
        :param dest: Optional default destination
        :type dest: str
        :param mtype: Optional default mediatype
        :type mtype: str
        :return: Found mediatype and destination
        :rtype: (bool, Location)

        """
        found = False
        for rule in self.rules:
            for rx in rule['rx']:
                match = rx.search(path.path)
                if match:
                    base = self.config.get('general', 'basepath')
                    if not rule['sorted']:
                        dest = join(base, rule['path'])
                    else:
                        dest = join(base, rule['path'], match.groupdict()['name'])
                    mtype = rule['name']
                    d = join(dest, path.basename)
                    if exists(d):
                        return False, False
                        # TODO Diff dir's semi intelligently
                        src = join(base, rule['path'], path)
                        d_size = get_size(d)
                        p_size = get_size(src)
                        if p_size == d_size:
                            self.log.info('Removing duplicate directory: {0}'.format(src))
                            rmtree(src)
                            return False, False
                        elif d_size < p_size:
                            self.log.info('Removing smaller destination directory: {0}'.format(d))
                            rmtree(d)
                            found = True
                        else:
                            return False, False
                    #else:
                        #print("Matched {0} -> {1}".format(rule['name'], path))
                    found = True
                if found: break
            if found: break
            
        if dest:
            # TODO move this to a separate method
            if not exists(dest):
                if self.config.getboolean('general', 'commit'):
                    mkdirp(dest)
                else:
                    self.log.info('Skipped creating directory: {0}'.format(dest))
            #releasePath = join(self.basePath, path)
            files = self.getReleaseFiles(path)
            if any(map(self.isLocked, files)):
                self.log.error("LOCKED!")
                mtype, dest = False, False
            else:
                log.debug("Found parent of {0} : {1}".format(path, dest))
            return mtype, Location(dest)
        else:
            return False, False

    def getReleaseFiles(self, folder, filelist=None):
        """ Get a list of files within the releases folder

        :param folder: Folder to look through
        :type folder: Location
        :param filelist: Optional list of files to append to
        :return: files found under the folder path
        :rtype: list
        """
        if not filelist:
            filelist = []
        if not exists(folder.path):
            raise OSError('Invalid path: {0}'.format(folder))
        for root, dirs, files in walk(folder.path):
            filelist.extend([ join(root, f) for f in files ])
        return filelist

    def isLocked(self, filename):
        """ Check to see if a file is in a locked state (in use)

        :param filename: File to check
        :type filename: str
        :return: Locked status
        :rtype: bool
        """
        try:
            file = open(filename, 'a+')
            if file:
                return False
            return True
        except IOError as err:
            log.exception(err)
            return True

    def execute(self):
        operations = self.filterNew()
        total_size = sum((cs.source.size for cs in operations))
        self.log.info('Total number of sorting changes: {0}'.format(len(operations)))
        self.log.info('Total changeset size: {0}'.format(friendlysize(total_size)))
        if self.config.getboolean('cleanup', 'enable', fallback=False):
            cleanups = self.cleanup()
            operations.extend(cleanups)
        return operations

    def cleanup(self):
        operations = []
        for section in self.config.filteredSections():
            newPath = join(self.config.get('general', 'basepath'), self.config.get(section, 'path'))
            for f in self.findCleanupFiles(newPath):
                file_path = Location(join(newPath, f))
                if self.config.getboolean('cleanup', 'delete_empty', fallback=False):
                    if isdir(str(file_path)):
                        if self.dirIsEmpty(file_path.path):
                            oper = ChangeSet.remove(file_path)
                            operations.append(oper)
        return operations


    def filterNew(self):
        # Execute Full Program
        #print(m.genFileList())
        changes = []
        for section in self.config.filteredSections():
            newPath = join(self.config.get('general', 'basepath'), self.config.get(section, 'path'))
            if not exists(newPath):
                self.log.warn('Skipping invalid section path: {0}'.format(newPath))
                continue
            self.setBasePath(newPath)
            self.log.info("Scanning {0}".format(newPath))
            file_list = self.genFileList()
            new_files = self.findNew(file_list)
            filtered_files = self.filterIgnored(new_files)
            for newp in filtered_files:
                mtype, path = self.findParentDir(newp)
                if mtype and path:
                    src = newp
                    dest = path
                    changes.append(ChangeSet(src, dest))
        return changes

def parse_path(path):
    """ Parse a path into separate pieces
    This probably doesnt work very well under windows?

    :param path: Path to parse
    :type path: str
    :return List of path pieces
    :rtype: list
    """
    return normpath(abspath(path)).split(sep)[1:]

def isOpen(filepath):
    pids=listdir('/proc')
    for pid in sorted(pids):
        try:
            int(pid)
        except ValueError:
            continue
        fd_dir=join('/proc', pid, 'fd')
        for file in listdir(fd_dir):
            try:
                link=readlink(join(fd_dir, file))
            except OSError:
                continue
            print(pid, link) 