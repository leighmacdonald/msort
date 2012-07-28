"""
Provides classes to perform actions against triggered files and folders
"""
from os import remove, makedirs, listdir
from os.path import isfile, isdir, exists, join, dirname
from shutil import move, rmtree

from msort import MSortError
from msort.log import getLogger
from msort.filesystem import dir_size, fmt_size

class OperationError(MSortError):
    """ Thrown on a error during a operantion """
    pass

class BaseOperation(object):
    """ Sets up the logger instance for the operation """

    def __init__(self):
        self.log = getLogger(__name__)

    def __call__(self):
        raise NotImplementedError('__call__ not implemented in {0}'.format(self.__str__()))

    def __str__(self):
        return self.__class__.__name__

class MoveOperation(BaseOperation):
    """ Used to move files from one directory to another"""

    def __init__(self, source, destination, create_dest=True):
        BaseOperation.__init__(self)
        self.source = source
        self.destination = destination
        self.create_dest = create_dest

    def __call__(self):
        try:
            dest_dir = dirname(self.destination)
            if self.create_dest and not exists(dest_dir):
                makedirs(dest_dir)
            move(self.source, self.destination)
        except Exception as err:
            raise OperationError(err)

    def __str__(self):
        return '{0} {1} {2}'.format(self.__class__.__name__, self.source, self.destination)

class MoveContentsOperation(MoveOperation):
    def __init__(self, source, destination, create_dest=True):
        MoveOperation.__init__(self, source, destination, create_dest)

    def __call__(self):
        ops = self._findOperations()
        for oper in ops:
            oper()


    def _findOperations(self):
        ops = []
        path_list = listdir(self.source)
        path_list.sort()
        for file_name in path_list:
            src_full = join(self.source, file_name)
            if isfile(src_full):
                dest_full = join(self.destination, file_name)
                ops.append(MoveOperation(src_full, dest_full, self.create_dest))
            else:
                self.log.debug('ASD')
        ops.append(DeleteOperation(self.source))
        return ops

class DeleteOperation(BaseOperation):
    """ Used to delete a path from the filesystem """

    def __init__(self, path):
        """ Set the path to be deleted

        :param path: Path to delete
        :type path: str
        """
        BaseOperation.__init__(self)
        self.source = path
        self.size = None

    def __call__(self):
        """ Perform the delete operation taking account for a directory or a folder
        being deleted
        """
        if isdir(self.source):
            rmtree(self.source)
            self.log.debug('Removed directory: {0}'.format(self.source))
        elif isfile(self.source):
            remove(self.source)
            self.log.debug('Removed file: {0}'.format(self.source))

    def __str__(self):
        if self.size == None:
            self.size = dir_size(self.source)
        return 'Delete ({0}) {1}'.format(fmt_size(self.size), self.source)

class OperationManager(dict):
    """
    Oversees executing queued up operations.
    """
    def __init__(self, error_continue=False):
        dict.__init__(self)
        self.log = getLogger(__name__)
        self.log.propagate = 1
        self.error_list = []
        self.error_continue = error_continue
        self.cur_idx = 0

    def executeSection(self, section):
        """ Perform all the operations under the section key provided

        :param section: Section key
        :type section: str
        :return: list of errors that may have occured
        :rtype: list
        """
        for oper in self[section]:
            self.cur_idx +=1
            self.log.info('[{1}/{2}] {0}'.format(str(oper), self.cur_idx, len(self)))
            try: oper()
            except OperationError as err:
                if not self.error_continue:
                    raise
                self.error_list.append(err)
        return self.error_list

    def execute(self, sections=None):
        """ Wrapper method to execute all the sections provided and return the overall
        execution status. If no sections are provided all the sections will be executed.

        :param sections: optional list of sections to map
        :type sections: None, list
        :return: Execution has errors status
        :rtype: bool
        """
        return not any(map(self.executeSection, sections if sections else self.keys()))

    def showErrors(self):
        """ Display all the error messages. """
        self.log.error('There were {0} errors encountered while executing all operations:'.format(len(self.error_list)))
        for i, error in enumerate(self.error_list):
            self.log.error('[{0}] {1}'.format(i, error))

    def __len__(self):
        """ Return the total numver of operations queued up for the dicts len

        :return: Total operations queued
        :rtype: int
        """
        return sum([len(x) for x in self.values()])

    def getType(self, operation_type):
        """ Get all the operations matching the supplied Type

        :param operation_type: Some type of BaseOperation
        :type operation_type: BaseOperation
        :return: Matching operations
        :rtype: list
        """
        found = []
        [found.extend(filterType(opers, operation_type)) for opers in self.values()]
        return found

def filterType(sequence, object_type):
    """ Get the sequence items matching the type supplied

    :param sequence: Sequence of things to check
    :type sequence: iter
    :param object_type: class name to match against
    :type object_type: any
    :return: filter instance of matched sequence items
    :rtype: filter
    """
    return filter(lambda o: type(o) == object_type,  sequence)