import re
def upperwords(word):
    return '.'.join(map(ucfirst, word.split('.')))

def ucfirst(word):
    if len(word) == 1: return word.upper()
    elif len(word) >= 2: return word[0].upper() + word[1:]
    else: return ''



def cleanup(word, sep='.'):
    word = sep.join(split_uc_words(word))
#    w = sep.join(word.split()).replace('-', sep)
#    w = w.replace('-', sep)
#    w = sep.join(sep.join(word.split()).replace('-', sep).split(sep))
    w = re.sub('\{0}+'.format(sep), sep, sep.join(sep.join(word.split()).replace('-', sep).split(sep)))
    if w.endswith(sep):
        w = w[0:len(w)-1]
    return upperwords(w)

def split_uc_words(words):
    """ Split a string using a forward look-ahead for upper case letters to act as word
    boundaries. If while iterating the next character will be upper case or if the current character is the last
    of the given string, then mark that as the end of the current word and add is to the new_words list to be
    returned.

    :param words: String of upper cased words to split eg: LongStringName
    :type words: string
    :return: List of words found eg: ['Long', 'String', 'Name']
    :rtype: list
    """
    size = len(words)-1
    new_words = []
    tmp_word = ''
    for i, c in enumerate(words):
        if i == 0 or c.isupper():
            # Make sure the first character is capitalized
            tmp_word += c.upper()
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


