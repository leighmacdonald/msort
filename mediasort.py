from logging import basicConfig, DEBUG, getLogger
from msort.conf import Config
from msort.filesystem import DirectoryScanner
from msort.check import DummyCheck
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck

basicConfig(level=DEBUG)
log = getLogger(__name__)
log.info('Initializing!')
conf = Config()

scanner = DirectoryScanner()
scanner.addChecker(DummyCheck())
scanner.addChecker(EmptyCheck())
scanner.addChecker(ReleaseCheck())
changes = scanner.find('/home/leigh/msort/test_root')
log.info(changes)