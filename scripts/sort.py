#!/bin/env python3
from sys import argv, exit
from os import stat
from os.path import expanduser, exists, join
from optparse import OptionParser
from logging import DEBUG
from msort import MSorter, Location, Config, ChangeSet, log, parse_path

# Configure
parser = OptionParser()
parser.add_option('-d', '--debug', dest="debug", action="store_true", default=False, help="Enable debugging output level")
parser.add_option('-t', '--test', dest="test", action="store_true", default=False, help="Test the changes without actually doing them")
parser.add_option('-c', '--commit', dest="commit", action="store_true", default=None, help="Commit the changes to disk")
parser.add_option('-e', '--error', dest="error", action="store_true", default=False, help="Continue on error")
parser.add_option('-C', '--cleanup', dest="cleanup", action="store_true", default=False, help="Remove any files matching the cleanup filters")
parser.add_option('-a', '--addrule', dest="addrule", metavar="REGEX", help="Add a new regex rule to the configuration")
parser.add_option('-l', '--listrule', dest="listrule", action="store_true", help="List currently loaded regex rules")
parser.add_option('-s', '--section', dest="section", metavar="SECTION", help="Set the section to use when performing operations")
options, args = parser.parse_args()

# Initialize
defaultPath = expanduser("~/Music")
path = argv[1] if len(argv) > 1 else defaultPath if exists(defaultPath) else expanduser("~/")
c = Config()
m = MSorter(config=c)

if options.debug:
    log.setLevel(DEBUG)
if options.test:
    c.set('general', 'commit', "false")
if options.commit:
    c.set('general', 'commit', "true")
if options.test and options.commit:
    log.fatal("Please only chose one of test (-t) or commit (-c)")
    exit(2)
if options.error:
    c.set('general','error_continue', "true")
if options.cleanup:
    c.set('cleanup', 'enable', 'true')
if options.addrule and not options.section:
    parser.error("-a (add) requires the -s (section) option to be set")
if options.addrule and options.section:
    c.addRule(options.section, options.addrule)
if options.listrule and not options.section:
    parser.error("-l (list) requires the -s (section) option to be set")
if options.listrule:
    log.info("Current regex pattern list ({0}):".format(options.section))
    print('+---+------------------------------------------------------------------------------------')
    for name, pattern in c.getRuleList(options.section.lower()):
        log.info('| {0} | {1} |'.format(name[2:], pattern))
    print('+---+------------------------------------------------------------------------------------')

    exit()
if args:
    for pa in args:
        if not exists(pa):
            log.warn("Skipping path not found: {0}".format(pa))
            continue

        pcs = parse_path(pa)
        p = pcs[len(pcs)-1:][0]
        mtype, path = m.findParentDir(p)
        if mtype and path:
            ChangeSet(p, path).exec(c.getboolean('general', 'commit'))

    exit()

commit = m.config.getboolean('general', 'commit')

# Execute Full Program
#print(m.genFileList())
changes = []
for section in c.filteredSections():
    newPath = Location(join(c.get('general', 'basepath'), c.get(section, 'path')), validate=False)
    if not newPath.exists():
        log.error('Skipping invalid section path: {0}'.format(newPath))
        continue
    m.setBasePath(newPath)
    log.info("Scanning {0}".format(newPath))
    for p in m.filterIgnored(m.findNew(m.genFileList())):
        mtype, path = m.findParentDir(p)
        if mtype and path:
            releasePath = join(m.basePath.path, p)
            changes.append(ChangeSet(releasePath, path))

    if options.cleanup or c.has_option('cleanup', 'enable') and c.getboolean('cleanup', 'enable'):
        log.debug('Starting cleanup')
        cs = [ChangeSet.remove(join(m.basePath.path, f)) for f in m.findCleanupFiles(newPath)]
        total = 0
        for x in cs:
            try:
                info = stat(x.source)
                x.exec(commit)
                total += info.st_size
            except Exception as err:
                log.exception(err)
        print("Total cleanup: {0}".format(total / 1024 / 1024))


for change in changes:
    try:
        change.exec(commit)
    except KeyboardInterrupt:
        log.fatal("Caught Ctrl+C, Bailing early!")
        exit(2)
    except Exception as err:
        log.exception(err)
        if c.getboolean('general', 'error_continue'):
            log.error(err)
            continue
        else:
            log.error("Bailing early, too many errors to continue")
            exit(2)