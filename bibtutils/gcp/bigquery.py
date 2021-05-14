'''
bibtutils.gcp.bigquery
~~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's BigQuery.

See the official BigQuery Python Client documentation here: `link <https://googleapis.dev/python/bigquery/latest/index.html>`_.

'''

from google.cloud import bigquery
from google.api_core import exceptions as google_exceptions
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def _run_bq_job(job):
    '''
    Helper method to run a BQ job and catch/print any errors.

    :type job: :class:`google.cloud.bigquery.job.*`
    :param job: the BigQuery job to run.
    '''
    try:
        job.result()
    except google_exceptions.BadRequest:
        logging.info(job.errors)
        raise SystemError(
            'Import failed with BadRequest exception. See error data in logs.')
    return


def upload_gcs_json(bucket_name, blob_name, bq_project, dataset, table, 
        append=True, ignore_unknown=True, autodetect_schema=False):
    '''
    Uploads a GCS blob in JSON NLD format to the specified table in BQ.
    
    Executing account must have both read permissions on the bucket/blob 
    and edit permissions on the dataset, in addition to the IAM bigquery 
    jobs user role in the project. NLD JSON file schema must match that
    of the destination table.

    Use :func:`~bibtutils.gcp.storage.write_gcs_nldjson` to get a properly
    formatted blob from JSON objects.

    .. code:: python

        from bibtutils.gcp.bigquery import upload_gcs_json
        upload_gcs_json(
            bucket_name='my_bucket',
            blob_name='my_nldjson_blob',
            bq_project='my_project',
            dataset='my_dataset',
            table='my_table'
        )

    :type bucket_name: :py:class:`str`
    :param bucket_name: the bucket hosting the specified blob.

    :type blob_name: :py:class:`str`
    :param blob_name: the blob to upload to BQ. must be in JSON NLD format.

    :type bq_project: :py:class:`str`
    :param bq_project: the project hosting the specified BQ dataset.

    :type dataset: :py:class:`str`
    :param dataset: the dataset hosting the specified table.

    :type table: :py:class:`str`
    :param table: the table to which to upload the blob.

    :type append: :py:class:`bool`
    :param append: (Optional) if true, will append to table. 
        if false, will overwrite. Defaults to ``True``.
    
    :type ignore_unknown: :py:class:`bool`
    :param ignore_unknown: (Optional) if true, will ignore values not 
        reflected in table schema while uploading. Defaults to ``True``.
        
    :type autodetect_schema: :py:class:`bool`
    :param autodetect_schema: (Optional) if true, will instruct BQ to 
        automatically detect the schema of the data being uploaded. Defaults to ``False``.
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
            autodetect=autodetect_schema,
            write_disposition = write_disp,
            source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            ignore_unknown_values = ignore_unknown
        )
    )

    _run_bq_job(load_job)
    
    logging.info(f'Upload of {source_uri} to BQ complete.')
    return


def query(query):
    '''
    Sends the user-supplied query to BQ and returns the result 
    as a list of dicts. The account running the query must have 
    Job Create permissions in the GCP Project and at least 
    Data Viewer on the target dataset.

    .. code:: python

        from bibtutils.gcp.bigquery import query
        fav_color_blue = query(
            'select name, favorite_color '
            'from `my_project.my_dataset.my_table` '
            'where favorite_color="blue"'
        )
        print(row['name'] for row in fav_color_blue)

    :type query: :py:class:`str`
    :param query: a full BQ query (e.g. ``'select * from `x.y.z` where a=b'``)

    :rtype: :py:class:`list`
    :returns: a list of dicts, one row in the result table per dict.
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
