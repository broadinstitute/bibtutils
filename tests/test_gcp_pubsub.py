import time
from .config import *
from bibtutils.gcp import pubsub


def test_pubsub():
    pubsub.send_pubsub(
        topic_uri=f'projects/{TEST_PROJECT}/topics/{TEST_PUBSUB}',
        payload='test payload for bibtutils pubsub'
    )
    
    pubsub.send_pubsub(
        topic_uri=f'projects/{TEST_PROJECT}/topics/{TEST_PUBSUB}',
        payload={
            'test': 'test_pubsub',
            'timestamp': int(time.time())
        }
    )