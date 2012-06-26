from os import listdir, readlink
from os.path import join

class MSortError(Exception):
    pass

def isOpen(filepath):
    pids=listdir('/proc')
    for pid in sorted(pids):
        try:
            int(pid)
        except ValueError:
            continue
        fd_dir=join('/proc', pid, 'fd')
        for file in listdir(fd_dir):
            try:
                link=readlink(join(fd_dir, file))
            except OSError:
                continue
            print(pid, link) 