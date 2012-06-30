"""
Provides tools related to calling system applications
"""
from subprocess import Popen, PIPE

def call_output(args):
    """ Call an application and return its output

    :param args: command like argument list (Popen)
    :type args: list
    :return: Command output
    :rtype: str
    """
    return Popen(args, stdout=PIPE).communicate()[0].strip()
