"""
bibtutils.gcp.storage
~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's Cloud Storage.

See the official Cloud Storage Python Client documentation here: `link <https://googleapis.dev/python/storage/latest/index.html>`_.

"""
import datetime
import json
import logging

from google.api_core import exceptions as google_exceptions
from google.cloud import storage

_LOGGER = logging.getLogger(__name__)


def create_bucket(project, bucket_name, location="US", credentials=None):
    """
    Creates a Google Cloud Storage bucket in the specified project.

    :type project: :py:class:`str`
    :param project: the project in which to create the bucket. The account
        being used **must** have "Storage Admin" rights on **the GCP project**.

    :type bucket_name: :py:class:`str`
    :param bucket_name: the name of the bucket to create. Note that
        bucket names must be **universally** unique in GCP, and need to
        adhere to the GCS bucket naming guidelines:
        https://cloud.google.com/storage/docs/naming-buckets

    :type location: (Optional) :py:class:`str`
    :param location: if specified, creates the dataset in the desired location/region.
        The locations and regions supported are listed in
        #locations_and_regions. if unspoecified
        https://cloud.google.com/bigquery/docs/locations
        defaults to US.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if not to
        use the account running the function for authentication.

    :rtype: :py:class:`gcp_storage:google.cloud.storage.bucket.Bucket`
    :returns:  The bucket created during this function call.
    """
    _LOGGER.info(
        f"Attempting to create bucket: [{bucket_name}] in project: [{project}]"
    )
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    try:
        bucket = client.create_bucket(bucket, project=project, location=location)
    except (google_exceptions.Forbidden,google_exceptions.Conflict, google_exceptions.BadRequest) as e:
        if google_exceptions.Forbidden:
            _LOGGER.error(
                "Current account does not have required permissions to create "
                f"buckets in GCP project: [{project}]. Navigate to "
                f"https://console.cloud.google.com/iam-admin/iam?project={project} "
                'and add the "Storage Admin" role to the appropriate account.'
            )
        raise e
    _LOGGER.info(f"Bucket: [{bucket.name}] created successfully.")
    return bucket


def read_gcs(bucket_name, blob_name, decode=True, credentials=None):
    """
    Reads the contents of a blob from GCS. Service account must
    have (at least) read permissions on the bucket/blob.

    Note that for **extremely** large files having ``decode=True``
    can increase runtime substantially.

    .. code:: python

        from bibtutils.gcp.storage import read_gcs
        data = read_gcs('my_bucket', 'my_blob')
        print(data)

    :type bucket_name: :py:class:`str`
    :param bucket_name: the bucket hosting the specified blob.

    :type blob_name: :py:class:`str`
    :param blob_name: the blob to read from GCS.

    :type decode: :py:class:`bool`
    :param decode: (Optional) whether or not to decode the blob
        contents into utf-8. Defaults to ``True``.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if not to
        use the account running the function for authentication.

    :rtype: :py:class:`str`
    :returns: blob contents, decoded to utf-8.
    """
    _LOGGER.info(f"Getting gs://{bucket_name}/{blob_name}")
    client = storage.Client(credentials=credentials)
    blob = client.get_bucket(bucket_name).get_blob(blob_name)
    contents = blob.download_as_bytes()
    if decode:
        return contents.decode("utf-8")
    return contents


def read_gcs_nldjson(bucket_name, blob_name, **kwargs):
    """
    Reads a blob in JSON NLD format from GCS and returns it as a list of dicts.
    Any extra arguments (``kwargs``) are passed to the :func:`~bibtutils.gcp.storage.read_gcs` function.

    .. code:: python

        from bibtutils.gcp.storage import read_gcs_nldjson
        data = read_gcs_nldjson('my_bucket', 'my_nldjson_blob')
        print(item['favorite_color'] for item in data)

    :type bucket_name: :py:class:`str`
    :param bucket_name: the bucket hosting the specified blob.

    :type blob_name: :py:class:`str`
    :param blob_name: the blob to read from GCS.

    :rtype: :py:class:`list`
    :returns: the data from the blob, converted into a list of :py:class:`dict`.
    """
    json_nld = read_gcs(bucket_name, blob_name, decode=True, **kwargs)
    _LOGGER.info("Converting from JSON NLD to JSON...")
    json_list = "[" + json_nld.replace("\n", ",")
    json_list = json_list.rstrip(",") + "]"
    return json.loads(json_list)


def write_gcs(
    bucket_name,
    blob_name,
    data,
    mime_type="text/plain",
    create_bucket_if_not_found=False,
    timeout=storage.constants._DEFAULT_TIMEOUT,
    credentials=None,
):
    """
    Writes a String to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.
    If ``data`` is a `str`, will be encoded as utf-8 before uploading.

    .. code:: python

        from bibtutils.gcp.storage import write_gcs
        write_gcs('my_bucket', 'my_blob', data='my favorite color is blue')

    :type bucket_name: :py:class:`str`
    :param bucket_name: the name of the bucket to which to write.

    :type blob_name: :py:class:`str`
    :param blob_name: the name of the blob to write.

    :type data: :py:class:`str` OR :py:class:`bytes`
    :param data: the data to be written.

    :type create_bucket_if_not_found: :py:class:`bool`
    :param create_bucket_if_not_found: (Optional) if ``True``, will attempt to
        create the bucket if it does not exist. Defaults to ``False``.

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if not to
        use the account running the function for authentication.

    :type content_type: :py:class:`str`
    :param content_type: (Optional) the
        `MIME type <https://www.iana.org/assignments/media-types/media-types.xhtml>`_
        being uploaded. defaults to ``'text/plain'``.
    """
    client = storage.Client(credentials=credentials)
    try:
        bucket = client.get_bucket(bucket_name)
    except google_exceptions.NotFound as e:
        _LOGGER.error(e.message)
        _LOGGER.info(f"create_bucket_if_not_found=={create_bucket_if_not_found}")
        if not create_bucket_if_not_found:
            raise e
        bucket = create_bucket(client.project, bucket_name)
    blob = bucket.blob(blob_name)
    _LOGGER.info(f"Writing to GCS: gs://{bucket_name}/{blob_name}")
    blob.upload_from_string(data, content_type=mime_type, timeout=timeout)
    _LOGGER.info("Upload complete.")
    return


def write_gcs_nldjson(bucket_name, blob_name, json_data, add_date=False, **kwargs):
    """
    Writes a dict to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.
    Use in conjunction with :func:`~bibtutils.gcp.bigquery.upload_gcs_json` to
    upload JSON data to BigQuery tables.
    Any extra arguments (``kwargs``) are passed to the :func:`~bibtutils.gcp.storage.write_gcs` function.

    .. code:: python

        from bibtutils.gcp.storage import write_gcs_nldjson
        write_gcs_nldjson(
            'my_bucket',
            'my_nldjson_blob',
            json_data=[
                {'name': 'leo', 'favorite_color': 'red'},
                {'name': 'matthew', 'favorite_color': 'blue'}
            ]
        )

    :type bucket_name: :py:class:`str`
    :param bucket_name: the name of the bucket to which to write.

    :type blob_name: :py:class:`str`
    :param blob_name: the name of the blob to write.

    :type json_data: :py:class:`list` OR :py:class:`dict`
    :param json_data: the data to be written. can be a list or a dict.
        will treat a dict as one row of data (and convert it to a one-item list).
        data will be converted to a JSON NLD formatted string
        before uploading for compatibility with
        :func:`~bibtutils.gcp.bigquery.upload_gcs_json`.

    :type add_date: :py:class:`bool`
    :param add_date: (Optional) whether or not to add upload date to
        the data before upload. Defaults to ``False``.

    :type create_bucket_if_not_found: :py:class:`bool`
    :param create_bucket_if_not_found: (Optional) if ``True``, will attempt to
        create the bucket if it does not exist. Defaults to ``False``.

    """
    nld_json = _generate_json_nld(json_data, add_date)
    write_gcs(bucket_name, blob_name, nld_json, **kwargs)
    return


def _generate_json_nld(json_data, add_date):
    """
    Takes a dict object and returns a string in JSON NLD format.
    Compatible with uploading to BQ.

    :type json_data: :py:class:`dict`
    :param json_data: the data to be converted to JSON NLD.

    :type add_date: :py:class:`bool`
    :param add_date: whether or not to add upload date to the
        data before upload.

    :rtype: :py:class:`str`
    :returns: formatted JSON NLD.
    """
    _LOGGER.info("Generating JSON NLD...")
    json_nld = ""
    if isinstance(json_data, dict):
        json_data = [json_data]
    for item in json_data:
        if add_date:
            item["upload_date"] = datetime.date.today().isoformat()
        json_nld += f"{json.dumps(item)}\n"
    _LOGGER.info("Generated.")
    return json_nld
