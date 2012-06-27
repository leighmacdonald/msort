from subprocess import Popen, PIPE

def call_output(args):
    return Popen(args, stdout=PIPE).communicate()[0].strip()

def isOpen(file_path):
    output = call_output(['lsof', file_path])
    return output