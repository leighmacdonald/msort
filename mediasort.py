#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
mediasort.py is a utility which can be used to sort directories and files into
normalized and group subfolders. Its primary purpose was to originally sort
downloaded media like TV shoes and movies. The naming conventions and packing
methods used for this often were varying. Some used periods '.' for spacers, some
used spaces, some underscore. Some were just single unpacked .avi files, and some
are archived in subdirectories. This tool attempts to normalize these names into
something that can be group against.

Copyright (c) 2012, Leigh MacDonald
License: MIT (see LICENSE for details)
"""
from sys import exit
from logging import basicConfig, DEBUG, INFO
from optparse import OptionParser

from msort.conf import Config, ConfigError
from msort.log import getLogger
from msort.filesystem import DirectoryScanner
from msort.operation import OperationError
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck
from msort.check.inuse import InUseCheck

# 3 doesnt have raw_input
try:     get_input = raw_input
except:  get_input = input
confirm = lambda m: get_input('{0} [Y/n]: '.format(m)).lower() in ('y', '')

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
    cur_idx = 0
    errors_list = []
    try:
        # Initialize the config file
        conf = Config(options.config_file)

        # Setup the scanner and register checkers to use
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(InUseCheck(conf))
        scanner.registerChecker(EmptyCheck(conf))
        scanner.registerChecker(ReleaseCheck(conf))
        changes = {}
        for section in conf.filteredSections():
            changes[section] = scanner.find(section)
        total_changes = sum([len(x) for x in changes.values()])
        log.info('Found {0} total changes to be executed'.format(total_changes))
        if options.autocommit or confirm('Apply changes found ({0})?'.format(total_changes)):

            for section, operations in changes.items():
                for oper in operations:
                    cur_idx +=1
                    log.info('[{1}/{2}] {0}'.format(str(oper), cur_idx, total_changes))
                    try:
                        oper()
                    except OperationError as err:
                        if not conf.getboolean('general', 'error_continue'):
                            raise
                        errors_list.append(err)
            if errors_list:
                log.error('There were {0} errors encountered while executing all operations:'.format(len(errors_list)))
                for i, error in enumerate(errors_list):
                    log.error('[{0}] {1}'.format(i, error))
            else:
                log.info('Completed all operations successfully! [{0}/{1}]'.format(cur_idx, total_changes))
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
        if total_changes and cur_idx == total_changes and not errors_list:
            log.info('All {0} operations completed successfully!'.format(total_changes))
        else:
            if errors_list:
                log.info('Errors were encountered, you should review them and make any changes deemed required.')
            else:
                log.info('No operations to perform were found.')
    return ret_code

if __name__ == "__main__":
    exit(main())
