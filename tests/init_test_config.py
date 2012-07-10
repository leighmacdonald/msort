"""
This is a simple helper module for the tests. It just generates a config file suitable for the
current location of the tests.
"""
from os import remove
from os.path import dirname, join, exists

def genConf():
    config_file = join(dirname(__file__), 'msort_test.conf')
    config_file_data = open(config_file, 'r').read().replace('^^TEST_DIR^^', join(dirname(__file__),'test_root'))
    temp_config_file = '{0}.temp'.format(config_file)
    if exists(temp_config_file):
        remove(temp_config_file)
    with open(temp_config_file, 'w') as config:
        config.write(config_file_data)
    from msort.conf import Config
    return Config(temp_config_file)

conf = genConf()
