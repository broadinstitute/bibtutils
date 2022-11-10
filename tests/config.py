import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ["GCP_SANDBOX_BIBTUTILS_TEST"]
TEST_PROJECT = 'bits-bt-sandbox'
TEST_SECRET = 'bibtutils-test-secret'
TEST_BUCKET = 'bibtutils-test-bucket'
TEST_DATASET = 'bibtutils_test_dataset'
TEST_TABLE = 'bibtutils_test_table'
TEST_PUBSUB = 'bibtutils-test-pubsub'