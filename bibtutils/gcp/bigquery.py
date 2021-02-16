from google.cloud import bigquery
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

def upload_gcs_json(bucket_name:str, blob_name:str, bq_project:str, dataset:str, table:str, append=True, ignore_unknown=True) -> None:
    '''
    Uploads a GCS blob in JSON NLD format to the specified table in BQ.
    Executing account must have both read permissions on the bucket/blob and edit permissions on the dataset, in addition to the IAM bigquery jobs user role in the project.

    Args:
        bucket_name (str): the bucket hosting the specified blob.
        blob_name (str): the blob to upload to BQ. must be in JSON NLD format.
        bq_project (str): the project hosting the specified BQ dataset.
        dataset (str): the dataset hosting the specified table.
        table (str): the table to which to upload the blob.
        append (bool, optional): if true, will append to table. if false, will overwrite. Defaults to True.
        ignore_unknown (bool, optional): if true, will ignore values not reflected in table schema while uploading. Defaults to True.
    '''
    # TODO: allow schema update options? https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.job.SchemaUpdateOption.html#google.cloud.bigquery.job.SchemaUpdateOption

    client = bigquery.Client()
    source_uri = f'gs://{bucket_name}/{blob_name}'
    table_ref = f'{bq_project}.{dataset}.{table}'
    logging.info(f'Uploading {source_uri} to {table_ref}...')
    if append:
        write_disp = bigquery.WriteDisposition.WRITE_APPEND
    else:
        write_disp =  bigquery.WriteDisposition.WRITE_TRUNCATE
    load_job = client.load_table_from_uri(
        source_uris = source_uri,
        destination = client.get_table(table_ref),
        job_config = bigquery.LoadJobConfig(
            write_disposition = write_disp,
            source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            ignore_unknown_values = ignore_unknown
        )
    )
    load_job.result()
    logging.info(f'Upload of {source_uri} to BQ complete.')
    return


def query(query:str) -> list:
    '''
    Sends the user-supplied query to BQ and returns the result as a list of dicts.
    The account running the query must have Job Create permissions in the GCP Project and at least Data Viewer on the target dataset.

    Args:
        query (str): A full BQ query (i.e. 'select * from `x.y.z` where a=b')

    Returns:
        list: A list of dicts, one row in the result table per dict.
    '''
    logging.debug(f'Sending query: {query}')
    bq_client = bigquery.Client()
    logging.info('Querying BQ...')
    query_job = bq_client.query(query)
    results = query_job.result()
    logging.info('Iterating over result rows...')
    results_json = []
    for row in results:
        results_json.append(dict(row.items()))
    logging.info('Returning results as list of dicts.')
    return results_json
