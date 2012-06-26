from logging import getLogger

class BaseCheck(object):
    def __init__(self):
        self.log = getLogger(__name__)

    def __call__(self, path):
        raise NotImplemented('__call__ method must be overridden.')

    def __str__(self):
        return self.__class__.__name__

class DummyCheck(BaseCheck):
    def __call__(self, path):
        return False