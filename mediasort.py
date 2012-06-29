#!/usr/bin/python
from sys import exit
from logging import basicConfig, DEBUG, INFO
from optparse import OptionParser

from msort.conf import Config, ConfigError
from msort.log import getLogger
from msort.filesystem import DirectoryScanner
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck
from msort.check.inuse import InUseCheck

confirm = lambda m: raw_input('{0} [Y/n]: '.format(m)).lower() in ('y', '')

def main():
    """ Parse command line arguments and run the sorter

    :return: Program exit code
    :rtype: int
    """
    # Parse CLI options
    parser = OptionParser(version='2.0')
    parser.add_option('-d', '--debug', dest="debug", action="store_true", default=False,
        help="Enable debugging output level")
    parser.add_option('-y', '--yes', dest="autocommit", action="store_true", default=False,
        help="Answer yes for all question, autocommit changes found")
    parser.add_option('-c', '--config', dest="config_file", default="~/.msort.conf", metavar='CONFIG_FILE',
        help="Set an alternate config file path")
    options, args = parser.parse_args()

    # Setup Logger
    log = getLogger(__name__)
    log_level = DEBUG if options.debug else INFO
    basicConfig(level=log_level, format='%(message)s')
    ret_code = 0
    try:
        # Initialize the config file
        conf = Config(options.config_file)

        # Setup the scanner and register checkers to use
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(InUseCheck(conf))
        scanner.registerChecker(EmptyCheck(conf))
        scanner.registerChecker(ReleaseCheck(conf))
        sections = conf.filteredSections()
        changes = {}
        for section in sections:
            changes[section] = scanner.find(section)
        total_changes = sum([len(x) for x in changes.values()])
        log.info('Found {0} total changes to be executed'.format(total_changes))
        if options.autocommit or confirm('Apply changes found ({0})?'.format(total_changes)):
            for section, operations in changes.iteritems():
                for oper in operations:
                    log.info('Executing: {0}'.format(str(oper)))
    except ConfigError as err:
        log.error('There was a configuration error:\n{0}'.format(err))
        ret_code = 3
    except KeyboardInterrupt:
        log.error('\b\bCaught Interrupt, fleeing!')
        ret_code = 2
    except Exception as err:
        log.exception(err)
        log.error('Tis but a flesh wound.')
        ret_code = 1
    else:
        log.info('With the speed of an African Swallow')
    return ret_code

if __name__ == "__main__":
    exit(main())