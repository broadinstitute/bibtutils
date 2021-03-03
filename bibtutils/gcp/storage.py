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


def write_gcs(bucket_name, blob_name, data, mime_type='text/plain'):
    '''
    Writes a String to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.

    :type bucket_name: :py:class:`str`
    :param bucket_name: the name of the bucket to which to write.

    :type blob_name: :py:class:`str`
    :param blob_name: the name of the blob to write.

    :type data: :py:class:`str`
    :param data: the data to be written.

    :type content_type: :py:class:`str`
    :param content_type: (Optional) the `MIME type <https://www.iana.org/assignments/media-types/media-types.xhtml>`_ being uploaded. defaults to ``'text/plain'``.
    '''
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).blob(blob_name)
    logging.info(f'Writing to GCS: gs://{bucket_name}/{blob_name}')
    blob.upload_from_string(data, content_type=mime_type)
    logging.info('Upload complete.')
    return


def read_gcs(bucket_name, blob_name, decode=True):
    '''
    Reads the contents of a blob from GCS. Service account must 
    have (at least) read permissions on the bucket/blob.

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


def write_gcs_nldjson(bucket_name, blob_name, json_data, add_date=False):
    '''
    Writes a dict to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.

    :type bucket_name: :py:class:`str`
    :param bucket_name: the name of the bucket to which to write.

    :type blob_name: :py:class:`str`
    :param blob_name: the name of the blob to write.

    :type json_data: :py:class:`dict`
    :param json_data: the data to be written. will be converted to 
        JSON NLD before uploading for compatibility with BQ.

    :type add_date: :py:class:`bool`
    :param add_date: (Optional) whether or not to add upload date to 
        the data before upload. Defaults to ``False``.
    '''
    nld_json = _generate_json_nld(json_data, add_date)
    write_gcs(bucket_name, blob_name, nld_json)
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
    for item in json_data:
        if add_date:
            item['upload_date'] = datetime.date.today().isoformat()
        json_nld += f'{json.dumps(item)}\n'
    logging.info('Generated.')
    return json_nld


def read_gcs_nldjson(bucket_name, blob_name):
    '''
    Reads a blob in JSON NLD format from GCS and returns it as a dict.

    :type bucket_name: :py:class:`str`
    :param bucket_name: the bucket hosting the specified blob.

    :type blob_name: :py:class:`str`
    :param blob_name: the blob to read from GCS.

    :rtype: :py:class:`dict`
    :returns: the data from the blob, converted into a dict object.
    '''
    json_nld = read_gcs(bucket_name, blob_name, decode=True)
    logging.info('Converting from JSON NLD to JSON...')
    json_list = '[' + json_nld.replace('\n', ',')
    json_list = json_list.rstrip(',') + ']'
    return json.loads(json_list)
