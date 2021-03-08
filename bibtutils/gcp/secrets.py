'''
bibtutils.gcp.secrets
~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's Secret Manager.

See the official Secret Manager Python Client documentation here: `link <https://googleapis.dev/python/secretmanager/latest/index.html>`_.

'''

from google.cloud import secretmanager
import json
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_secret(host_project, secret_name):
    '''
    An alias for :func:`~bibtutils.gcp.secrets.get_secret_json`.

    .. code:: python

        from bibtutils.gcp.secrets import get_secret
        secret = get_secret('my_project', 'my_secret')
        print(secret['password'])

    :type host_project: :py:class:`str`
    :param host_project: the name of the host project of the secret.

    :type secret_name: :py:class:`str`
    :param secret_name: the name of the secret to fetch.

    :rtype: :py:class:`dict`
    :returns: the secret data.
    '''
    return get_secret_json(host_project, secret_name)


def get_secret_json(host_project, secret_name):
    '''
    Gets a secret from GCP and returns it parsed into a dict.
    Executing account must have (at least) secret version accessor 
    permissions on the secret. Note: secret must be in JSON format.

    .. code:: python

        from bibtutils.gcp.secrets import get_secret_json
        secret = get_secret_json('my_project', 'my_secret')
        print(secret['password'])

    :type host_project: :py:class:`str`
    :param host_project: the name of the host project of the secret.

    :type secret_name: :py:class:`str`
    :param secret_name: the name of the secret to fetch.

    :rtype: :py:class:`dict`
    :returns: the secret data.
    '''
    secret = get_secret_by_name(host_project, secret_name, decode=True)
    return json.loads(secret)


def get_secret_by_name(host_project, secret_name, decode=True):
    '''
    Gets a secret from GCP and returns it either as decoded 
    utf-8 or raw bytes (depending on `decode` parameter).
    Executing account must have (at least) secret version 
    accessor permissions on the secret.

    .. code:: python

        from bibtutils.gcp.secrets import get_secret_by_name
        secret = get_secret_by_name('my_project', 'my_secret')
        print(secret)

    :type host_project: :py:class:`str`
    :param host_project: the name of the host project of the secret.

    :type secret_name: :py:class:`str`
    :param secret_name: the name of the secret to fetch.

    :type decode: :py:class:`bool`
    :param decode: (Optional) whether or not to decode the bytes. 
        Defaults to ``True``.

    :rtype: :py:class:`bytes` OR :py:class:`str`
    :returns: the secret data.
    '''
    secret_uri = f'projects/{host_project}/secrets/{secret_name}/versions/latest'
    return get_secret_by_uri(secret_uri, decode=decode)


def get_secret_by_uri(secret_uri, decode=True):
    '''
    Gets a secret from GCP and returns it either as decoded 
    utf-8 or raw bytes (depending on ``decode`` parameter).
    Executing account must have (at least) secret version 
    accessor permissions on the secret.

    .. code:: python

        from bibtutils.gcp.secrets import get_secret_by_uri
        secret = get_secret_by_uri(
            'projects/my_project/secrets/my_secret/versions/latest'
        )
        print(secret)

    :type secret_uri: :py:class:`str`
    :param secret_uri: the uri of the secret to fetch. secret uri format: 
        ``'projects/{host_project}/secrets/{secret_name}/versions/latest'``
    
    :type decode: :py:class:`bool`
    :param decode: (Optional) whether or not to decode the bytes. 
        Defaults to ``True``.

    :rtype: :py:class:`bytes` OR :py:class:`str`
    :returns: the secret data.
    '''
    logging.info(f'Getting secret: {secret_uri}')
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={'name':secret_uri}, timeout=3).payload.data
    if decode:
        return secret.decode('utf-8')
    return secret

