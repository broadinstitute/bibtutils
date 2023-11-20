"""
bibtutils.gcp.bigquery
~~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's BigQuery.

See the official BigQuery Python Client documentation here:
`link <https://googleapis.dev/python/bigquery/latest/index.html>`_.

"""
import logging

from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery

_LOGGER = logging.getLogger(__name__)


def create_dataset(
    bq_project,
    dataset_name,
    description=None,
    location="US",
    credentials=None,
    **kwargs,
):
    """
    Creates a dataset in BigQuery using the specified parameters.

    Any extra args (``kwargs``) are passed to
        :py:func:`gcp_bigquery:google.cloud.bigquery.client.Client.create_dataset`.

    :type bq_project: :py:class:`str`
    :param bq_project: the project in which to find the dataset.

    :type dataset_name: :py:class:`str`
    :param dataset_name: the name of the dataset to be created.

    :type description: (Optional) :py:class:`str`
    :param description: the description for the datset. if unspecified defaults to None

    :type location: (Optional) :py:class:`str`
    :param location: if specified, creates the dataset in the desired location/region.
        The locations and regions supported are listed in
        #locations_and_regions. if unspoecified
        https://cloud.google.com/bigquery/docs/locations
        defaults to US.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if not
        to use the account running the function for authentication.

    """
    dataset_id = f"{bq_project}.{dataset_name}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location
    dataset.description = description

    _LOGGER.info(f"Attempting to create dataset: {dataset_id}")
    _LOGGER.info("Sending dataset API request...")
    try:
        client = bigquery.Client(project=bq_project, credentials=credentials)
        dataset = client.create_dataset(dataset, timeout=30, **kwargs)
        _LOGGER.info(f"Dataset created: {dataset_id}")
    except (
        google_exceptions.NotFound,
        google_exceptions.GoogleAPICallError,
        google_exceptions.PermissionDenied,
    ) as e:
        if google_exceptions.PermissionDenied:
            _LOGGER.error(
                "Current account does not have required permissions to create "
                f"bigquery table in GCP project: [{bq_project}]. Navigate to "
                f"https://console.cloud.google.com/iam-admin/iam?project={bq_project} "
                'and add the "BigQuery User" role to the appropriate account.'
            )
        raise e
    return


def delete_dataset(
    bq_project,
    dataset_name,
    delete_contents=False,
    not_found_ok=False,
    credentials=None,
    **kwargs,
):
    """
    Creates a dataset in BigQuery using the specified parameters.

    Any extra args (``kwargs``) are passed to
        :py:func:`gcp_bigquery:google.cloud.bigquery.client.Client.create_dataset`.

    :type bq_project: :py:class:`str`
    :param bq_project: the project in which to find the dataset.

    :type dataset_name: :py:class:`str`
    :param dataset_name: the name of the dataset to be created.

    :type delete_contents: (Boolean) :py:class:`str`
    :param delete_contents: The boolean that decides to delete the dataset.
        if unspecified defaults to False where in the dataset is not deleted
        if it contains tables within.

    :type not_found_ok: (Boolean) :py:class:`str`
    :param not_found_ok: Boolean used to control errors if dataset is not found.
        if unspecified defaults to False where in errors are not suppressed.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.

    """
    dataset_id = f"{bq_project}.{dataset_name}"

    _LOGGER.info(f"Attempting to delete dataset: {dataset_id}")
    _LOGGER.info("Sending dataset API request...")
    try:
        client = bigquery.Client(project=bq_project, credentials=credentials)
        client.delete_dataset(
            dataset_id,
            delete_contents=delete_contents,
            not_found_ok=not_found_ok,
            **kwargs,
        )
        _LOGGER.info(f"Dataset deleted: {dataset_id}")
    except (
        google_exceptions.NotFound,
        google_exceptions.GoogleAPICallError,
        google_exceptions.PermissionDenied,
    ) as e:
        if google_exceptions.PermissionDenied:
            _LOGGER.error(
                "Current account does not have required permissions to create "
                f"bigquery table in GCP project: [{bq_project}]. Navigate to "
                f"https://console.cloud.google.com/iam-admin/iam?project={bq_project} "
                'and add the "BigQuery User" role to the appropriate account.'
            )
        raise e
    return


def create_table(
    bq_project,
    dataset,
    table,
    schema_json=[],
    time_partitioning_interval=None,
    time_partitioning_field=None,
    credentials=None,
    **kwargs,
):
    """
    Creates a table in BigQuery using the specified parameters.

    Any extra args (``kwargs``) are passed to the
        :py:func:`gcp_bigquery:google.cloud.bigquery.client.Client.create_table` method.

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
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'``

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

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.
    """
    table_id = f"{bq_project}.{dataset}.{table}"
    _LOGGER.info(f"Attempting to create table: {table_id}")
    schema_structs = []
    if schema_json and len(schema_json) > 0:
        _LOGGER.info("Building schema...")
        schema_structs = _generate_schema_struct(schema_json)
        _LOGGER.info("Schema built.")
    _LOGGER.info("Sending create_table API request...")
    client = bigquery.Client(project=bq_project, credentials=credentials)
    table = bigquery.Table(table_id, schema=schema_structs)
    if time_partitioning_interval or time_partitioning_field:
        _LOGGER.info(
            f"Partioning specified [{time_partitioning_interval}/"
            f"{time_partitioning_field}]. Configuring..."
        )
        partitioning_interval = None
        if time_partitioning_interval:
            if time_partitioning_interval.upper() == "HOUR":
                partitioning_interval = bigquery.TimePartitioningType.HOUR
            if time_partitioning_interval.upper() == "DAY":
                partitioning_interval = bigquery.TimePartitioningType.DAY
            if time_partitioning_interval.upper() == "MONTH":
                partitioning_interval = bigquery.TimePartitioningType.MONTH
            if time_partitioning_interval.upper() == "YEAR":
                partitioning_interval = bigquery.TimePartitioningType.YEAR
        table.time_partitioning = bigquery.TimePartitioning(
            type_=partitioning_interval, field=time_partitioning_field
        )
    table = client.create_table(table, **kwargs)
    _LOGGER.info(f"Table created: {table_id}")
    return


def delete_table(bq_project, dataset, table, credentials=None, **kwargs):
    """
    Method to delete a given table.

    Any extra args (``kwargs``) are passed to the
        :py:func:`gcp_bigquery:google.cloud.bigquery.client.Client.delete_table` method.

    :type bq_project: :py:class:`str`
    :param bq_project: the bq project where the dataset lives.

    :type dataset: :py:class:`str`
    :param dataset: the bq dataset where the table lives.

    :type table: :py:class:`str`
    :param table: the bq table to delete.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.
    """
    table_id = f"{bq_project}.{dataset}.{table}"
    _LOGGER.info(f"Attempting to delete table: {table_id}")
    client = bigquery.Client(project=bq_project, credentials=credentials)
    client.delete_table(table_id, **kwargs)
    _LOGGER.info(f"Table deleted: {table_id}")
    return


def _get_schema(bq_project, dataset, table):
    """
    Helper method to return the schema of a given table.

    :type bq_project: :py:class:`str`
    :param bq_project: the bq project where the dataset lives.

    :type dataset: :py:class:`str`
    :param dataset: the bq dataset where the table lives.

    :type table: :py:class:`str`
    :param table: the bq table to fetch the schema for.
    """
    client = bigquery.Client(project=bq_project)
    table = client.get_table(f"{bq_project}.{dataset}.{table}")
    return table.schema


def _generate_schema(bucket_name, blob_name, bq_project, dataset, credentials=None):
    """
    Helper method to get an auto-generated schema based on input data in a bucket. Note
    that this will create and delete a temporary table in order to generate the schema.

    :type bucket_name: :py:class:`str`
    :param bucket_name: the location of the input data to generate a schema for.

    :type blob_name: :py:class:`str`
    :param blob_name: the input data to generate a schema for.

    :type bq_project: :py:class:`str`
    :param bq_project: the bq project in which to make the temporary table.

    :type dataset: :py:class:`str`
    :param dataset: the bq dataset in which to make the temporary table.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.
    """
    create_and_upload(
        bucket_name,
        blob_name,
        bq_project,
        dataset,
        "temp_table_autodetect_schema",
        autodetect_schema=True,
        ignore_unknown=False,
        credentials=credentials,
    )
    schema = _get_schema(
        bq_project, dataset, "temp_table_autodetect_schema", credentials=credentials
    )
    delete_table(
        bq_project, dataset, "temp_table_autodetect_schema", credentials=credentials
    )
    return schema


def _generate_schema_struct(schema_json):
    """
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
    """
    schema_structs = []
    for column in schema_json:
        if "fields" in column.keys():
            struct = bigquery.SchemaField(
                column["name"],
                column["type"],
                mode=column.get("mode", "NULLABLE"),
                description=column.get("description", None),
                fields=_generate_schema_struct(column["fields"]),
            )
        else:
            struct = bigquery.SchemaField(
                column["name"],
                column["type"],
                mode=column.get("mode", "NULLABLE"),
                description=column.get("description", None),
            )
        schema_structs.append(struct)
    return schema_structs


def _monitor_job(job):
    """
    Helper method to monitor a BQ job and catch/print any errors.

    :type job: :py:class:`bq_storage:google.cloud.bigquery.job.*`
    :param job: the BigQuery job to run.
    """
    try:
        job.result()
    except google_exceptions.BadRequest:
        _LOGGER.error(job.errors)
        raise SystemError(
            "Import failed with BadRequest exception. See error data in logs."
        )
    return


def upload_gcs_json(
    bucket_name,
    blob_name,
    bq_project,
    dataset,
    table,
    append=True,
    ignore_unknown=True,
    autodetect_schema=False,
    schema_json=None,
    credentials=None,
    await_result=True,
    **kwargs,
):
    """
    Uploads a GCS blob in JSON NLD format to the specified table in BQ.

    Executing account must have both read permissions on the bucket/blob
    and edit permissions on the dataset, in addition to the IAM bigquery
    jobs user role in the project. NLD JSON file schema must match that
    of the destination table.

    Use :func:`~bibtutils.gcp.storage.write_gcs_nldjson` to get a properly
    formatted blob from JSON objects.

    Any extra args (``kwargs``) are passed to
        :py:func:`gcp_bigquery:google.cloud.bigquery.client.Client.load_table_from_uri`.

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
        automatically detect the schema of the data being uploaded.
        Defaults to ``False``.

    :type schema_json: :py:class:`dict`
    :param schema_json: (Optional) the schema for the new table. Defaults
        to an empty list (no schema). The format of the schema should be
        identical to what is returned by
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'``

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.

    :type await_result: :py:class:`bool`
    :param await_result: Whether or not to hang and await the job result or
        simply return None once the job is submitted.
    """
    source_uri = f"gs://{bucket_name}/{blob_name}"
    table_ref = f"{bq_project}.{dataset}.{table}"
    schema_struct = None
    if schema_json:
        if autodetect_schema:
            _LOGGER.warn(
                'You currently have "autodetect_schema" set to True while '
                'also specifying a schema. Consider setting "autodetect_schema" '
                "to False to avoid type inference conflicts."
            )
        _LOGGER.info("Building schema...")
        schema_struct = _generate_schema_struct(schema_json)
        _LOGGER.info("Schema built.")
    _LOGGER.info(f"Uploading {source_uri} to {table_ref}...")
    if append:
        write_disp = bigquery.WriteDisposition.WRITE_APPEND
    else:
        write_disp = bigquery.WriteDisposition.WRITE_TRUNCATE
    client = bigquery.Client(project=bq_project, credentials=credentials)
    load_job = client.load_table_from_uri(
        source_uris=source_uri,
        destination=client.get_table(table_ref),
        job_config=bigquery.LoadJobConfig(
            autodetect=autodetect_schema,
            write_disposition=write_disp,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            ignore_unknown_values=ignore_unknown,
            schema=schema_struct,
        ),
        **kwargs,
    )

    if await_result:
        _monitor_job(load_job)
        _LOGGER.info(f"Upload of {source_uri} to BQ complete.")

    return


def create_and_upload(
    bucket_name,
    blob_name,
    bq_project,
    dataset,
    table,
    append=True,
    ignore_unknown=True,
    autodetect_schema=False,
    schema_json=None,
    generate_schema=False,
    time_partitioning_interval=None,
    time_partitioning_field=None,
    already_created_ok=False,
    credentials=None,
    await_result=True,
):
    """
    Combines the functionality of :func:`~bibtutils.gcp.bigquery.create_table`
    and :func:`~bibtutils.gcp.bigquery.upload_gcs_json`. You may
    specify whether upload should proceed if the table already exists. You may
    also either specify the desired schema or ask BQ to autodetect the schema.

    Note this function does NOT support ``kwargs``.

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
        ``bq show --format=prettyjson project:dataset.table | jq '.schema.fields'``

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

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.

    :type await_result: :py:class:`bool`
    :param await_result: Whether or not to hang and await the job result or
        simply return None once the job is submitted.
    """
    _LOGGER.info("Starting create_and_upload...")
    if not schema_json and not autodetect_schema and not generate_schema:
        err_msg = (
            "You did not specify a schema AND did not instruct "
            'BigQuery to infer the schema. Please either set "schema_json" in '
            'the function call or set "autodetect_schema" to True.'
        )
        _LOGGER.error(err_msg)
        raise Exception(err_msg)
    elif generate_schema:
        schema_json = _generate_schema(
            bucket_name, blob_name, bq_project, dataset, credentials=credentials
        )
    try:
        create_table(
            bq_project,
            dataset,
            table,
            schema_json=schema_json,
            time_partitioning_interval=time_partitioning_interval,
            time_partitioning_field=time_partitioning_field,
            credentials=credentials,
        )
    except google_exceptions.Conflict as e:
        if not already_created_ok:
            raise e

    upload_gcs_json(
        bucket_name,
        blob_name,
        bq_project,
        dataset,
        table,
        append=append,
        ignore_unknown=ignore_unknown,
        autodetect_schema=autodetect_schema,
        schema_json=schema_json,
        credentials=credentials,
        await_result=await_result,
    )

    _LOGGER.info("create_and_upload completed successfully.")
    return


def query(query, query_project=None, credentials=None, await_result=True):
    """
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

    :type query_project: :py:class:`str`
    :param query_project: the ID of the project in which to run the query.
        If not specified, defaults to the environment's credential's project.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if
        not to use the account running the function for authentication.

    :type await_result: :py:class:`bool`
    :param await_result: Whether or not to hang and await the job result or
        simply return None once the job is submitted.

    :rtype: :py:class:`list`
    :returns: a list of dicts, one row in the result table per dict.
    """
    _LOGGER.debug(f"Sending query: {query}")
    bq_client = bigquery.Client(project=query_project, credentials=credentials)
    _LOGGER.info("Querying BQ...")
    query_job = bq_client.query(query)
    if not await_result:
        _LOGGER.debug("Not waiting for result of query, returning None.")
        return None
    results = query_job.result()
    _LOGGER.info("Iterating over result rows...")
    results_json = []
    for row in results:
        results_json.append(dict(row.items()))
    _LOGGER.info("Returning results as list of dicts.")
    return results_json
