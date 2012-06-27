from logging import StreamHandler, DEBUG, getLogger as realGetLogger, Formatter
from colorama import Fore, Back, init, Style


class ColourStreamHandler(StreamHandler):

    colours = {
        'DEBUG' : Fore.CYAN,
        'INFO' : Fore.GREEN,
        'WARN' : Fore.YELLOW,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRIT' : Back.RED + Fore.WHITE,
        'CRITICAL' : Back.RED + Fore.WHITE
    }

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                stream.write(self.colours[record.levelname] + message + Style.RESET_ALL)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def getLogger(name=None):
    log = realGetLogger(name)
    formatter = Formatter('%(message)s')
    handler = ColourStreamHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(DEBUG)
    log.propagate = 0
    return log