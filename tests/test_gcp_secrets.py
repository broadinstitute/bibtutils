from .config import *
from bibtutils.gcp import secrets

def test_secrets_plaintext():
    expected = '{"field1": "value1", "field2": 2}'
    secret = secrets.get_secret_by_name(TEST_PROJECT, TEST_SECRET)
    assert secret == expected
    secret = secrets.get_secret_by_uri(f'projects/{TEST_PROJECT}/secrets/{TEST_SECRET}/versions/latest')
    assert secret == expected
    
def test_secrets_nldjson():
    expected = {'field1': 'value1', 'field2': 2}
    secret = secrets.get_secret(TEST_PROJECT, TEST_SECRET)
    assert secret == expected
    secret = secrets.get_secret_json(TEST_PROJECT, TEST_SECRET)
    assert secret == expected