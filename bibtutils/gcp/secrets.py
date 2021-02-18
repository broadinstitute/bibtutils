'''
bibtutils.gcp.secrets
~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's Secret Manager.

'''

from google.cloud import secretmanager
import json
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_secret(host_project, secret_name):
    '''
    An alias for :func:`~bibtutils.gcp.secrets.get_secret_json`.

    :type host_project: `str`
    :param host_project: the name of the host project of the secret.

    :type secret_name: `str`
    :param secret_name: the name of the secret to fetch.

    :rtype: `dict`
    :returns: the secret data.
    '''
    return get_secret_json(host_project, secret_name)


def get_secret_json(host_project, secret_name):
    '''
    Gets a secret from GCP and returns it parsed into a dict.
    Executing account must have (at least) secret version accessor 
    permissions on the secret. Note: secret must be in JSON format.

    :type host_project: `str`
    :param host_project: the name of the host project of the secret.

    :type secret_name: `str`
    :param secret_name: the name of the secret to fetch.

    :rtype: `dict`
    :returns: the secret data.
    '''
    secret_uri = f'projects/{host_project}/secrets/{secret_name}/versions/latest'
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()

    secret = client.access_secret_version(
        request={'name':secret_uri}, 
        timeout=3
    ).payload.data.decode('UTF-8')

    return json.loads(secret)


def get_secret_by_name(host_project, secret_name, decode=True):
    '''
    Gets a secret from GCP and returns it either as decoded 
    utf-8 or raw bytes (depending on `decode` parameter).
    Executing account must have (at least) secret version 
    accessor permissions on the secret.

    :type host_project: `str`
    :param host_project: the name of the host project of the secret.

    :type secret_name: `str`
    :param secret_name: the name of the secret to fetch.

    :type decode: `bool`
    :param decode: (Optional) whether or not to decode the bytes. 
        Defaults to ``True``.

    :rtype: `bytes` OR `str`
    :returns: the secret data.
    '''
    secret_uri = f'projects/{host_project}/secrets/{secret_name}/versions/latest'
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={'name':secret_uri}, timeout=3).payload.data
    if decode:
        return secret.decode('utf-8')
    return secret


def get_secret_by_uri(secret_uri, decode=True):
    '''
    Gets a secret from GCP and returns it either as decoded 
    utf-8 or raw bytes (depending on `decode` parameter).
    Executing account must have (at least) secret version 
    accessor permissions on the secret.

    :type secret_uri: `str`
    :param secret_uri: the uri of the secret to fetch. secret uri format: 
        `projects/{host_project}/secrets/{secret_name}/versions/latest`
    
    :type decode: `bool`
    :param decode: (Optional) whether or not to decode the bytes. 
        Defaults to ``True``.

    :rtype: `bytes` OR `str`
    :returns: the secret data.
    '''
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={'name':secret_uri}, timeout=3).payload.data
    if decode:
        return secret.decode('utf-8')
    return secret

