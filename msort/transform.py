import re
def upperwords(word):
    return '.'.join(map(ucfirst, word.split('.')))

def ucfirst(word):
    return word[0].upper() + word[1:]


def cleanup(word, sep='.'):
    w = sep.join(word.split()).replace('-', sep)
    w = w.replace('-', sep)
    w = sep.join(sep.join(word.split()).replace('-', sep).split(sep))
    w = re.sub('\{0}+'.format(sep), sep, sep.join(sep.join(word.split()).replace('-', sep).split(sep)))
    if w.endswith(sep):
        w = w[0:len(w)-1]

    return upperwords(w)