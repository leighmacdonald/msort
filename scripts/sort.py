#!/bin/env python3
"""
sort.py -- A command line implementation for the msort module.

"""
from sys import argv, exit
from os import stat, rmdir
from os.path import expanduser, exists, join
from optparse import OptionParser
from logging import DEBUG
from msort import MSorter, Location, Config, ChangeSet, log, parse_path, friendlysize

# Configure
parser = OptionParser(version="%prog 1.0", description=__doc__)
parser.add_option('-d', '--debug', dest="debug", action="store_true", default=False, help="Enable debugging output level")
parser.add_option('-t', '--test', dest="test", action="store_true", default=False, help="Test the changes without actually doing them")
parser.add_option('-c', '--commit', dest="commit", action="store_true", default=None, help="Commit the changes to disk")
parser.add_option('-e', '--error', dest="error", action="store_true", default=False, help="Continue on error")
parser.add_option('-C', '--cleanup', dest="cleanup", action="store_true", default=False, help="Remove any files matching the cleanup filters")
parser.add_option('-E', '--empty', dest="cleanup_empty", action="store_true", default=False, help="Remove empty directories found")
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
if options.cleanup_empty:
    c.set('cleanup', 'delete_empty', "true")
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
    log.info('+---+------------------------------------------------------------------------------------')
    for name, pattern in c.getRuleList(options.section.lower()):
        log.info('| {0} | {1} |'.format(name[2:], pattern))
    log.info('+---+------------------------------------------------------------------------------------')

    exit()
if args:
    for pa in args:
        if not exists(pa):
            log.warn("Skipping path not found: {0}".format(pa))
            continue

        pcs = parse_path(pa)
        p = pcs[len(pcs)-1:][0]
        mediatype, parent = m.findParentDir(p)
        if mediatype and parent:
            cs = ChangeSet(p, path)
            cs(commit=c.getboolean('general', 'commit'))

    exit()

commit = m.config.getboolean('general', 'commit')

# Execute Full Program
#print(m.genFileList())
changes = []
for section in c.filteredSections():
    newPath = join(c.get('general', 'basepath'), c.get(section, 'path'))
    if not exists(newPath):
        log.error('Skipping invalid section path: {0}'.format(newPath))
        continue
    m.setBasePath(newPath)
    log.info("Scanning {0}".format(newPath))
    for newp in m.filterIgnored(m.findNew(m.genFileList())):
        mtype, path = m.findParentDir(newp)
        if mtype and path:
            changes.append(ChangeSet(join(m.basePath, newp), path))
        #else: continue
    if options.cleanup or c.has_option('cleanup', 'enable') and c.getboolean('cleanup', 'enable'):
        if c.has_option('cleanup', 'delete_empty') and c.getboolean('cleanup', 'delete_empty'):
            if m.dirIsEmpty(newPath):
                if commit:
                    log.debug('Removing empty path: {0}'.format(newPath))
                    rmdir(newPath)
                else:
                    log.info('Removing empty path: {0}'.format(newPath))
                continue
        for f in m.findCleanupFiles(newPath):
            oper = ChangeSet.remove(join(m.basePath, f))
            changes.append(oper)

total = 0
if changes:
    log.debug('Starting cleanup')
    for change in changes:
        try:
            if change.oper == 'remove':
                total += stat(change.source).st_size
            change(commit=commit)
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
    log.info("Total cleanup: {0}".format(friendlysize(total)))