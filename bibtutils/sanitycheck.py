'''
bibtutils.sanitycheck
~~~~~~~~~~~~~~~~~~~~~

Otherwise useless functions used to make sure the package is working properly.
'''

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

def testfunc():
    '''A test function which prints to stdout and logs a message to the logger.

    :rtype: `NoneType`
    :returns: Nothing.
    '''
    logging.info('Hello world')
    print('Hello world')
    return
