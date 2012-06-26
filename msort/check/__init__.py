from logging import getLogger

class BaseCheck(object):
    def __init__(self, config):
        self.log = getLogger(__name__)
        self.conf = config

    def __call__(self, section, path):
        raise NotImplemented('__call__ method must be overridden.')

    def __str__(self):
        return self.__class__.__name__

class DummyCheck(BaseCheck):
    def __call__(self, section, path):
        return False