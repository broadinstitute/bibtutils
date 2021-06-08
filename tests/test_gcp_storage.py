from .config import *
import time
from uuid import uuid4
from bibtutils.gcp import storage

    
def test_storage_create_bucket():
    bucket_name = 'bibtutils-test-temp-' + str(uuid4())
    storage.create_bucket(TEST_PROJECT, bucket_name)
    
    # cleanup
    from google.cloud import storage as gcs
    gcs.Client().get_bucket(bucket_name).delete()
    
def test_storage_plaintext():
    test_timestamp = int(time.time())
    test_data = 'Test data for plaintext GCS interactions.'
    test_blob = f'test-gcs-plaintext-{test_timestamp}'
    storage.write_gcs(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        data=test_data,
        mime_type='text/plain',
        create_bucket_if_not_found=True
    )
    rcvd_data = storage.read_gcs(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        decode=True
    )
    assert rcvd_data == test_data
    

def test_storage_nldjson():
    test_timestamp = int(time.time())
    test_data = [
        {
            'test_name': 'test_storage_nldjson', 
            'test_desc': 'Test data for NLD JSON GCS interactions.', 
            'timestamp': test_timestamp
        },
        {
            'test_name': 'test_storage_nldjson_r2', 
            'test_desc': 'Test data for NLD JSON GCS interactions. Row 2.', 
            'timestamp': test_timestamp
        }
    ]
    test_blob = f'test-gcs-nldjson-{test_timestamp}.nldjson'
    storage.write_gcs_nldjson(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        json_data=test_data,
        add_date=True,
    )
    rcvd_data = storage.read_gcs_nldjson(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
    )
    assert rcvd_data == test_data
    