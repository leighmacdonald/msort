from subprocess import Popen, PIPE

def call_output(args):
    return Popen(args, stdout=PIPE).communicate()[0].strip()
