from logging import StreamHandler, DEBUG, getLogger as realGetLogger, Formatter, INFO


try:
    from colorama import Fore, Back, init, Style

    class ColourStreamHandler(StreamHandler):
        """ A colorized output SteamHandler """

        # Some basic colour scheme defaults
        colours = {
            'DEBUG' : Fore.CYAN + Style.DIM,
            'INFO' : Fore.GREEN,
            'WARN' : Fore.YELLOW,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRIT' : Back.RED + Fore.WHITE,
            'CRITICAL' : Back.RED + Fore.WHITE
        }

        @property
        def is_tty(self):
            """ Check if we are using a "real" TTY. If we are not using a TTY it means that
            the colour output should be disabled.

            :return: Using a TTY status
            :rtype: bool
            """
            try: return getattr(self.stream, 'isatty', None)()
            except: return False

        def emit(self, record):
            """ Write out a multi coloured log record based on the log level.

            :param record: unformatted log message
            :type record: LogRecord
            :raises: KeyBoardError, SystemExit
            """
            try:
                message = self.format(record)
                if not self.is_tty:
                    self.stream.write(message)
                else:
                    self.stream.write(self.colours[record.levelname] + message + Style.RESET_ALL)
                self.stream.write(getattr(self, 'terminator', '\n'))
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    has_colour = True
except:
    has_colour = False

# Logging instance cache
loggers = {}
log_level = INFO

def getLogger(name=None, fmt='%(message)s'):
    """ Get and initialize a colourised logging instance if the system supports
    it as defined by the log.has_colour

    :param name: Name of the logger
    :type name: str
    :param fmt: Message format to use
    :type fmt: str
    :return: Logger instance
    :rtype: Logger
    """
    global loggers, log_level

    try: return loggers[name]
    except KeyError:
        logger = realGetLogger(name)
        logger.setLevel(log_level)
        # Only enable colour if support was loaded properly
        handler = ColourStreamHandler() if has_colour else StreamHandler()
        handler.setFormatter(Formatter(fmt))
        logger.addHandler(handler)
        loggers[name] = logger
        return logger

def setLevel(level):
    """ Set the global log level

    :param level: logging module log level to set
    :type level: int
    """
    global log_level, loggers

    [logger.setLevel(level) for logger in loggers.values()]
    log_level = level