'''
bibtutils.gcp.storage
~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's Cloud Storage.

See the official Cloud Storage Python Client documentation here: `link <https://googleapis.dev/python/storage/latest/index.html>`_.

'''

from google.cloud import storage
import datetime
import logging
import json

logging.getLogger(__name__).addHandler(logging.NullHandler())


def read_gcs(bucket_name, blob_name, decode=True):
    '''
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

    :rtype: :py:class:`str`
    :returns: blob contents, decoded to utf-8.
    '''
    logging.info(f'Getting gs://{bucket_name}/{blob_name}')
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).get_blob(blob_name)
    contents = blob.download_as_bytes()
    if decode:
        return contents.decode('utf-8')
    return contents



def read_gcs_nldjson(bucket_name, blob_name):
    '''
    Reads a blob in JSON NLD format from GCS and returns it as a list of dicts.

    .. code:: python

        from bibtutils.gcp.storage import read_gcs_nldjson
        data = read_gcs_nldjson('my_bucket', 'my_nldjson_blob')
        print(item['favorite_color'] for item in data)

    :type bucket_name: :py:class:`str`
    :param bucket_name: the bucket hosting the specified blob.

    :type blob_name: :py:class:`str`
    :param blob_name: the blob to read from GCS.

    :rtype: :py:class:`list`
    :returns: the data from the blob, converted into a list of dicts.
    '''
    json_nld = read_gcs(bucket_name, blob_name, decode=True)
    logging.info('Converting from JSON NLD to JSON...')
    json_list = '[' + json_nld.replace('\n', ',')
    json_list = json_list.rstrip(',') + ']'
    return json.loads(json_list)



def write_gcs(bucket_name, blob_name, data, mime_type='text/plain', timeout=storage.constants._DEFAULT_TIMEOUT):
    '''
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

    :type content_type: :py:class:`str`
    :param content_type: (Optional) the 
        `MIME type <https://www.iana.org/assignments/media-types/media-types.xhtml>`_ 
        being uploaded. defaults to ``'text/plain'``.
    '''
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).blob(blob_name)
    logging.info(f'Writing to GCS: gs://{bucket_name}/{blob_name}')
    blob.upload_from_string(data, content_type=mime_type, timeout=timeout)
    logging.info('Upload complete.')
    return



def write_gcs_nldjson(bucket_name, blob_name, json_data, add_date=False, timeout=storage.constants._DEFAULT_TIMEOUT):
    '''
    Writes a dict to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.
    Use in conjunction with :func:`~bibtutils.gcp.bigquery.upload_gcs_json` to 
    upload JSON data to BigQuery tables.

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
    '''
    nld_json = _generate_json_nld(json_data, add_date)
    write_gcs(bucket_name, blob_name, nld_json, timeout=timeout)
    return



def _generate_json_nld(json_data, add_date):
    '''
    Takes a dict object and returns a string in JSON NLD format. 
    Compatible with uploading to BQ.

    :type json_data: :py:class:`dict`
    :param json_data: the data to be converted to JSON NLD.

    :type add_date: :py:class:`bool`
    :param add_date: whether or not to add upload date to the 
        data before upload.

    :rtype: :py:class:`str`
    :returns: formatted JSON NLD.
    '''
    logging.info('Generating JSON NLD...')
    json_nld = ''
    if isinstance(json_data, dict):
        json_data = [json_data]
    for item in json_data:
        if add_date:
            item['upload_date'] = datetime.date.today().isoformat()
        json_nld += f'{json.dumps(item)}\n'
    logging.info('Generated.')
    return json_nld