import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

def testfunc():
    logging.info('Hello world')
    print('Hello world')
    return
