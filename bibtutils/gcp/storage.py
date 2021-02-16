from google.cloud import storage
import logging
import json

logging.getLogger(__name__).addHandler(logging.NullHandler())


def write_gcs(bucket_name:str, blob_name:str, data:str) -> None:
    '''
    Writes a String to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.

    Args:
        bucket_name (str): the name of the bucket to which to write.
        blob_name (str): the name of the blob to write.
        data (str): the data to be written.
    '''
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).blob(blob_name)
    logging.info(f'Writing to GCS: gs://{bucket_name}/{blob_name}')
    blob.upload_from_string(data)
    logging.info('Upload complete.')
    return


def read_gcs(bucket_name:str, blob_name:str, decode=True) -> (str or bytes):
    '''
    Reads the contents of a blob from GCS. Service account must have (at least) read permissions on the bucket/blob.

    Args:
        bucket_name (str): the bucket hosting the specified blob.
        blob_name (str): the blob to read from GCS.
        decode (bool, optional): whether or not to decode the blob contents into utf-8. Defaults to True.

    Returns:
        str: blob contents, decoded to utf-8.
    '''
    logging.info(f'Getting gs://{bucket_name}/{blob_name}')
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).get_blob(blob_name)
    contents = blob.download_as_bytes()
    if decode:
        return contents.decode('utf-8')
    return contents


def write_gcs_nldjson(bucket_name:str, blob_name:str, json_data:str, add_date=False) -> None:
    '''
    Writes a dict to GCS storage under a given blob name to the given bucket.
    The executing account must have (at least) write permissions to the bucket.

    Args:
        bucket_name (str): the name of the bucket to which to write.
        blob_name (str): the name of the blob to write.
        json_data (dict): the data to be written. will be converted to JSON NLD before uploading for compatibility with BQ.
        add_date (bool, optional): whether or not to add upload date to the data before upload. Defaults to False.
    '''
    nld_json = _generate_json_nld(json_data)
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name, timeout=3).blob(blob_name)
    logging.info(f'Dumping to storage {blob_name}...')
    blob.upload_from_string(nld_json, add_date=add_date)
    return


def _generate_json_nld(json_data:dict, add_date:bool) -> str:
    '''
    Takes a dict object and returns a string in JSON NLD format. Compatible with uploading to BQ.

    Args:
        json_data (dict): the data to be converted to JSON NLD.
        add_date (bool): whether or not to add upload date to the data before upload.

    Returns:
        String: formatted JSON NLD.
    '''
    logging.info('Generating JSON NLD...')
    json_nld = ''
    for item in json_data:
        if add_date:
            item['upload_date'] = datetime.date.today().isoformat()
        json_nld += f'{json.dumps(item)}\n'
    logging.info('Generated.')
    return json_nld


def read_gcs_nldjson(bucket_name:str, blob_name:str) -> dict:
    '''
    Reads a blob in JSON NLD format from GCS and returns it as a dict.

    Args:
        bucket_name (str): the bucket hosting the specified blob.
        blob_name (str): the blob to read from GCS.

    Returns:
        dict: the data from the blob, converted into a dict object.
    '''
    logging.info(f'Getting gs://{bucket_name}/{blob_name}')
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).get_blob(blob_name)
    json_nld = blob.download_as_string().decode('utf-8')
    logging.info('Converting from JSON NLD to JSON...')
    json_list = '[' + json_nld.replace('\n', ',')
    json_list = json_list.rstrip(',') + ']'
    return json.loads(json_list)
