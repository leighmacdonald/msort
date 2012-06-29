from os import remove
from os.path import isfile, isdir
from shutil import move, rmtree

from msort.log import getLogger
from msort import MSortError
from msort.filesystem import dir_size, fmt_size

class OperationError(MSortError):
    pass

class BaseOperation(object):
    def __init__(self):
        self.log = getLogger(__name__)

    def __call__(self):
        raise NotImplementedError('__call__ not implemented in {0}'.format(self.__str__()))

    def __str__(self):
        return self.__class__.__name__

class MoveOperation(BaseOperation):
    def __init__(self, source, destination):
        BaseOperation.__init__(self)
        self.source = source
        self.destination = destination

    def __call__(self):
        try:
            move(self.source, self.destination)
        except Exception as err:
            raise OperationError(err)

    def __str__(self):
        return '{0} {1} {2}'.format(self.__class__.__name__, self.source, self.destination)

class DeleteOperation(BaseOperation):
    def __init__(self, path):
        BaseOperation.__init__(self)
        self.source = path
        self.size = None

    def __call__(self):
        if isdir(self.source):
            rmtree(self.source)
            self.log.info('Removed directory: {0}'.format(self.source))
        elif isfile(self.source):
            remove(self.source)
            self.log.info('Removed file: {0}'.format(self.source))
        else:
            raise OperationError('Invalid path type, must be dir or file: {0}'.format(self.source))

    def __str__(self):
        if not self.size:
            self.size = dir_size(self.source)
        return '{0} ({1}) {2}'.format(fmt_size(self.size), self.__class__.__name__, self.source)
