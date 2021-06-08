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


def create_table(bq_project, dataset, table, schema_json=[], 
        time_partitioning_interval=None, time_partitioning_field=None):
    '''
    Creates a table in BigQuery using the specified parameters. 

    :type bq_project: :py:class:`str`
    :param bq_project: the project in which to find the dataset.

    :type dataset: :py:class:`str`
    :param dataset: the dataset in which to create the table.

    :type table: :py:class:`str`
    :param table: the name of the table to create.

    :type schema_json: :py:class:`dict`
    :param schema_json: (Optional) the schema for the new table. Defaults 
        to an empty list (no schema). The format of the schema should be 
        identical to what is returned by 
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'
    
    :type time_partitioning_interval: :py:class:`str`
    :param time_partitioning_interval: (Optional) if specified, will 
        create the table with the time partitioning interval desired. 
        Only recognizes values of: ``HOUR``, ``DAY``, ``MONTH``, or ``YEAR``.
        Capitalization doesn't matter. If value is unrecognized, this parameter 
        will simply be ignored. Defaults to ``None``.
        
    :type time_partitioning_field: :py:class:`str`
    :param time_partitioning_field: (Optional) if specified, will create 
        the table with time partitioning on the desired field. Any 
        value specified must match a **top-level** ``DATE``, ``DATETIME``, or 
        ``TIMESTAMP`` field in the table. If also specifying ``HOUR`` as the 
        partition interval, this parameter cannot be ``DATE``. The field 
        must also be ``NULLABLE`` or ``REQUIRED`` according to the schema. 
        Defaults to ``None``.
    '''
    table_id = f'{bq_project}.{dataset}.{table}'
    logging.info(f'Creating table: {table_id}')
    client = bigquery.Client()
    schema_structs = []
    if schema_json and len(schema_json) > 0:
        schema_structs = _generate_schema_struct(schema_json)
    logging.info('Sending create_table API request...')
    table = bigquery.Table(table_id, schema=schema_structs)
    if time_partitioning_interval or time_partitioning_field:
        logging.info('Partioning specified. Configuring...')
        partitioning_interval = None
        if time_partitioning_interval:
            if time_partitioning_interval.upper() == 'HOUR': partitioning_interval = bigquery.TimePartitioningType.HOUR
            if time_partitioning_interval.upper() == 'DAY': partitioning_interval = bigquery.TimePartitioningType.DAY
            if time_partitioning_interval.upper() == 'MONTH': partitioning_interval = bigquery.TimePartitioningType.MONTH
            if time_partitioning_interval.upper() == 'YEAR': partitioning_interval = bigquery.TimePartitioningType.YEAR
        table.time_partitioning = bigquery.TimePartitioning(
            type_=partitioning_interval,
            field=time_partitioning_field
        )
    table = client.create_table(table)
    logging.info(f'Table created: {table_id}')
    return


def _generate_schema_struct(schema_json):
    '''
    Helper method to take a BigQuery schema in JSON format and convert it 
    to an array of :py:class:`gcp_bigquery:google.cloud.bigquery.SchemaFields` 
    objects for use with the BQ API.
    
    :type schema_json: :py:class:`dict`
    :param schema_json: the schema for the new table. The format of 
        the schema should be identical to what is returned by 
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'
    
    :rtype: :py:class:`list`
    :returns: A list of :py:class:`gcp_bigquery:google.cloud.bigquery.SchemaFields` 
        objects corresponding to the specified schema.
    '''
    schema_structs = []
    logging.info('Building schema...')
    for column in schema_json:
        schema_structs.append(
            bigquery.SchemaField(
                column['name'], 
                column['type'], 
                mode=column.get('mode', 'NULLABLE'),
                description=column.get('description', None)
            )
        )
    logging.info('Schema built.')
    return schema_structs


def _run_bq_job(job):
    '''
    Helper method to run a BQ job and catch/print any errors.

    :type job: :py:class:`bq_storage:google.cloud.bigquery.job.*`
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
        append=True, ignore_unknown=True, autodetect_schema=False, schema_json=None):
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

    :type schema_json: :py:class:`dict`
    :param schema_json: (Optional) the schema for the new table. Defaults 
        to an empty list (no schema). The format of the schema should be 
        identical to what is returned by 
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'
    '''
    # TODO: allow schema update options? https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.job.SchemaUpdateOption.html#google.cloud.bigquery.job.SchemaUpdateOption

    source_uri = f'gs://{bucket_name}/{blob_name}'
    table_ref = f'{bq_project}.{dataset}.{table}'
    schema_struct = None
    if schema_json:
        if autodetect_schema:
            logging.warn(
                'You currently have "autodetect_schema" set to True while '
                'also specifying a schema. Consider setting "autodetect_schema" '
                'to False to avoid type inference conflicts.'
            )
        schema_struct = _generate_schema_struct(schema_json)
    logging.info(f'Uploading {source_uri} to {table_ref}...')
    if append:
        write_disp = bigquery.WriteDisposition.WRITE_APPEND
    else:
        write_disp =  bigquery.WriteDisposition.WRITE_TRUNCATE
    client = bigquery.Client()
    load_job = client.load_table_from_uri(
        source_uris = source_uri,
        destination = client.get_table(table_ref),
        job_config = bigquery.LoadJobConfig(
            autodetect=autodetect_schema,
            write_disposition=write_disp,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            ignore_unknown_values=ignore_unknown,
            schema=schema_struct
        )
    )

    _run_bq_job(load_job)
    
    logging.info(f'Upload of {source_uri} to BQ complete.')
    return


def create_and_upload(bucket_name, blob_name, bq_project, dataset, table, 
        append=True, ignore_unknown=True, autodetect_schema=False, 
        schema_json=None, time_partitioning_interval=None, 
        time_partitioning_field=None, already_created_ok=False):
    '''
    Combines the functionality of :func:`~bibtutils.gcp.bigquery.create_table` 
    and :func:`~bibtutils.gcp.bigquery.upload_gcs_json`. You may
    specify whether upload should proceed if the table already exists. You may 
    also either specify the desired schema or ask BQ to autodetect the schema.

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
        automatically detect the schema of the data being uploaded. 
        Defaults to ``False``. Should be set to False if ``schema_json`` 
        is defined.

    :type schema_json: :py:class:`dict`
    :param schema_json: (Optional) the schema for the new table. Defaults 
        to an empty list (no schema). The format of the schema should be 
        identical to what is returned by 
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'

    :type time_partitioning_interval: :py:class:`str`
    :param time_partitioning_interval: (Optional) if specified, will 
        create the table with the time partitioning interval desired. 
        Only recognizes values of: ``HOUR``, ``DAY``, ``MONTH``, or ``YEAR``.
        Capitalization doesn't matter. If value is unrecognized, this parameter 
        will simply be ignored. Defaults to ``None``.
        
    :type time_partitioning_field: :py:class:`str`
    :param time_partitioning_field: (Optional) if specified, will create 
        the table with time partitioning on the desired field. Any 
        value specified must match a **top-level** ``DATE``, ``DATETIME``, or 
        ``TIMESTAMP`` field in the table. The field must also be ``NULLABLE``
        or ``REQUIRED`` according to the schema. Defaults to ``None``.
    
    :type already_created_ok: :py:class:`bool`
    :param already_created_ok: (Optional) whether or not to proceed with data upload 
        if the table already exists. Defaults to ``False`` (will fail if table exists).
    '''
    logging.info('Starting create_and_upload...')
    if not schema_json and not autodetect_schema:
        err_msg = (
            'You did not specify a schema AND did not instruct '
            'BigQuery to infer the schema. Please either set "schema_json" in '
            'the function call or set "autodetect_schema" to True.'
        )
        logging.error(err_msg)
        raise Exception(err_msg)
    try:
        create_table(
            bq_project, dataset, table, schema_json=schema_json,
            time_partitioning_interval=time_partitioning_interval,
            time_partitioning_field=time_partitioning_field
        )
    except google_exceptions.Conflict as e:
        if not already_created_ok: raise e
    
    upload_gcs_json(
        bucket_name, blob_name, bq_project, dataset, table, 
        append=append, ignore_unknown=ignore_unknown, 
        autodetect_schema=autodetect_schema, schema_json=schema_json
    )
    
    logging.info('create_and_upload completed successfully.')
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
