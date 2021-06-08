from .config import *
import time
from datetime import date
from bibtutils.gcp import bigquery, storage

def test_bigquery():
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
    test_blob = f'test-bq-upload-{test_timestamp}.nldjson'
    storage.write_gcs_nldjson(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        json_data=test_data,
        add_date=True,
    )
    bigquery.upload_gcs_json(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        bq_project=TEST_PROJECT,
        dataset=TEST_DATASET,
        table=TEST_TABLE,
        append=True,
        ignore_unknown=False,
        autodetect_schema=True
    )
    rcvd_data = bigquery.query(
        f'select * from `{TEST_PROJECT}.{TEST_DATASET}.{TEST_TABLE}` '
        f'where timestamp={test_timestamp}'
    )
    for i in range(len(test_data)):
        test_data[i]['upload_date'] = date.today()
    assert rcvd_data == test_data

def test_bigquery_create_table():
    test_schema = [
        {
            'name': 'test_name',
            'mode': 'REQUIRED',
            'type': 'STRING'
        },
        {
            'name': 'upload_date',
            'mode': 'NULLABLE',
            'type': 'DATE'
        }
    ]
    bigquery.create_table(
        TEST_PROJECT, TEST_DATASET, 'test_create_table',
        schema_json=test_schema,
        time_partitioning_interval='HOUR',
    )
    
    # cleanup
    from google.cloud import bigquery as bq
    bq.Client().delete_table(f'{TEST_PROJECT}.{TEST_DATASET}.test_create_table', not_found_ok=False)


def test_bigquery_create_and_upload():
    test_timestamp = int(time.time())
    test_data = [
        {
            'test_name': 'test_create_upload', 
            'test_desc': 'Test data for NLD JSON GCS table create/upload.',
            'timestamp': test_timestamp
        },
        {
            'test_name': 'test_create_upload_r2',
            'test_desc': 'Test data for NLD JSON GCS table create/upload. Row 2.',
            'timestamp': test_timestamp
        }
    ]
    test_schema = [
        {
            'name': 'test_name',
            'mode': 'REQUIRED',
            'type': 'STRING'
        },
        {
            'name': 'test_desc',
            'mode': 'NULLABLE',
            'type': 'STRING'
        },
        {
            'name': 'timestamp',
            'mode': 'NULLABLE',
            'type': 'INTEGER'
        },
        {
            'name': 'upload_date',
            'mode': 'NULLABLE',
            'type': 'DATE'
        }
    ]
    test_blob = f'test-bq-create-and-upload-{test_timestamp}.nldjson'
    storage.write_gcs_nldjson(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        json_data=test_data,
        add_date=True,
    )
    # prep
    from google.cloud import bigquery as bq
    client = bq.Client()
    client.delete_table(f'{TEST_PROJECT}.{TEST_DATASET}.test_create_upload_table', not_found_ok=True)
    
    # test
    bigquery.create_and_upload(
        bucket_name=TEST_BUCKET,
        blob_name=test_blob,
        bq_project=TEST_PROJECT, 
        dataset=TEST_DATASET, 
        table='test_create_upload_table',
        append=False,
        ignore_unknown=False,
        autodetect_schema=True,
        schema_json=test_schema,
        time_partitioning_interval='DAY',
        time_partitioning_field='upload_date',
        already_created_ok=False
    )
    
    # cleanup
    client.delete_table(f'{TEST_PROJECT}.{TEST_DATASET}.test_create_upload_table', not_found_ok=False)

