from logging import StreamHandler, DEBUG, getLogger as realGetLogger, Formatter

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
    global loggers

    try: return loggers[name]
    except KeyError:
        loggers[name] = realGetLogger(name)
        # Only enable colour if support was loaded properly
        handler = ColourStreamHandler() if has_colour else StreamHandler()
        handler.setFormatter(Formatter(fmt))
        loggers[name].addHandler(handler)
        return loggers[name]