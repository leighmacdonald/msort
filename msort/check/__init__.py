from msort.log import getLogger

from msort import MSortError

class CheckError(MSortError):
    pass

class CheckSkip(CheckError):
    pass

class BaseCheck(object):
    """
    Base instance to be overridden by a check plugin
    """
    def __init__(self, config):
        """ Setup the logger and configuration values

        :param config: Configuration Instance
        :type config: Config
        """
        self.log = getLogger(__name__)
        self.conf = config

    def __call__(self, section, path):
        """ Base method that must be overridden

        :param section: Section name being used
        :type section: str
        :param path: Full path of the path to be checked
        :type path: str
        :raises: NotImplemented
        :rtype:
        """
        raise NotImplemented('__call__ method must be overridden.')

    def __str__(self):
        return self.__class__.__name__

class DummyCheck(BaseCheck):
    """ Dummy check used for testing only """

    def __call__(self, section, path): return False