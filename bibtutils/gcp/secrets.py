from google.cloud import secretmanager
import json
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_secret(host_project:str, secret_name:str) -> dict:
    '''
    An alias for `get_secret_json`.
    Gets a secret from GCP and returns it parsed into a dict.
    Executing account must have (at least) secret version accessor permissions on the secret.
    Note: secret must be in JSON format.

    Args:
        host_project (str): the name of the host project of the secret.
        secret_name (str): the name of the secret to fetch.

    Returns:
        dict: the secret data.
    '''
    return get_secret_json(host_project, secret_name)


def get_secret_json(host_project:str, secret_name:str) -> dict:
    '''
    Gets a secret from GCP and returns it parsed into a dict.
    Executing account must have (at least) secret version accessor permissions on the secret.
    Note: secret must be in JSON format.

    Args:
        host_project (str): the name of the host project of the secret.
        secret_name (str): the name of the secret to fetch.

    Returns:
        dict: the secret data.
    '''
    secret_uri = f'projects/{host_project}/secrets/{secret_name}/versions/latest'
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={'name':secret_uri}, timeout=3).payload.data.decode('UTF-8')
    return json.loads(secret)


def get_secret_by_name(host_project:str, secret_name:str, decode=True) -> (bytes or str):
    '''
    Gets a secret from GCP and returns it either as decoded utf-8 or raw bytes (depending on `decode` parameter).
    Executing account must have (at least) secret version accessor permissions on the secret.

    Args:
        host_project (str): the name of the host project of the secret.
        secret_name (str): the name of the secret to fetch.
        decode (bool, optional): whether or not to decode the bytes. Defaults to True.

    Returns:
        bytes OR str: the secret data.
    '''
    secret_uri = f'projects/{host_project}/secrets/{secret_name}/versions/latest'
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={'name':secret_uri}, timeout=3).payload.data
    if decode:
        return secret.decode('utf-8')
    return secret


def get_secret_by_uri(secret_uri:str, decode=True) -> (bytes or str):
    '''
    Gets a secret from GCP and returns it either as decoded utf-8 or raw bytes (depending on `decode` parameter).
    Executing account must have (at least) secret version accessor permissions on the secret.

    Args:
        secret_uri (str): the uri of the secret to fetch. secret uri format: `projects/{host_project}/secrets/{secret_name}/versions/latest`
        decode (bool, optional): whether or not to decode the bytes. Defaults to True.

    Returns:
        bytes OR str: the secret data.
    '''
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={'name':secret_uri}, timeout=3).payload.data
    if decode:
        return secret.decode('utf-8')
    return secret

