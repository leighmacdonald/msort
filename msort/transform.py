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

def splitucwords(words):
    size = len(words)-1
    new_words = []
    tmp_word = ''
    for i, c in enumerate(words):
        if i == 0 or c.isupper():
            tmp_word += c
        else:
            if i+1 <= size:
                if words[i+1].isupper():
                    # Next character is uppercase, so this is the end of the current word
                    tmp_word += c
                    new_words.append(tmp_word)
                    tmp_word = ''
                else:
                    tmp_word += c
            else:
                tmp_word += c
                new_words.append(tmp_word)
    return new_words


