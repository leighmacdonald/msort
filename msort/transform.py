"""
String transformations used to try and normalize different naming schemes.
"""
import re

default_sep = '.'
default_spacers = ('.', ' ', '_')

def upperwords(word, sep=default_sep):
    """ Split a string by the seperator value and uppercase transform the first character
    of each sequence item then joining the string again and returning it.

    :param sep: String to operatre on
    :type sep: str
    :param word: Word seperator character
    :type word: str
    :return: Uppercased words string
    :rtype: str
    """
    return sep.join(map(ucfirst, word.split(sep)))

def ucfirst(word):
    """ Capitialize the first letter of the string given

    :param word: String to capitalize
    :type word: str
    :return: Capitalized string
    :rtype: str
    """
    return word.upper() if len(word) == 1 else word[0].upper() + word[1:] if word else word

def cleanup(word, sep=default_sep):
    """ This function will take several steps to attempt to "clean" the input string to a
     more usable and uniform format.

     It currently does the following steps:


    :param word: String of words to clean
    :type word: str
    :param sep: Separator character to use
    :type sep: str
    :return: Cleaned and formatted string
    :rtype: str
    """
    word = sep.join(split_uc_words(word))
    word = word.replace('\'', '')
    w = re.sub('\{0}+'.format(sep), sep, sep.join(sep.join(word.split()).replace('-', sep).split(sep)))
    if w.endswith(sep):
        w = w[0:len(w)-1]
    return upperwords(w)

def split_uc_words(words):
    """ Split a string using a forward look-ahead for upper case letters to act as word
    boundaries. If while iterating the next character will be upper case or if the current character is the last
    of the given string, then mark that as the end of the current word and add is to the new_words list to be
    returned.

    :param words: String of upper cased words to split eg. LongStringName
    :type words: string
    :return: List of words found eg: ['Long', 'String', 'Name']
    :rtype: str[]
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
                if c in default_spacers:
                    new_words.append(tmp_word)
                    tmp_word = ''
                elif words[i+1].isupper():
                    # Next character is uppercase, so this is the end of the current word
                    tmp_word += c
                    new_words.append(tmp_word)
                    tmp_word = ''
                else:
                    tmp_word += c
            else:
                tmp_word += c
                new_words.append(tmp_word)
    if not new_words and tmp_word:
        return [tmp_word]
    return new_words


