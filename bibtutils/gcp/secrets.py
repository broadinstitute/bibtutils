"""
bibtutils.gcp.secrets
~~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's Secret Manager.

See the official Secret Manager Python Client documentation here: `link <https://googleapis.dev/python/secretmanager/latest/index.html>`_.

"""
import json
import logging

from google.cloud import secretmanager

_LOGGER = logging.getLogger(__name__)


def get_secret(host_project, secret_name, **kwargs):
    """
    An alias for :func:`~bibtutils.gcp.secrets.get_secret_json`.
    Any extra arguments (``kwargs``) are passed to the :func:`~bibtutils.gcp.secrets.get_sercret_by_uri` function.

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
    """
    return get_secret_json(host_project, secret_name, **kwargs)


def get_secret_json(host_project, secret_name, **kwargs):
    """
    Gets a secret from GCP and returns it parsed into a dict.
    Executing account must have (at least) secret version accessor
    permissions on the secret. Note: secret must be in JSON format.
    Any extra arguments (``kwargs``) are passed to the :func:`~bibtutils.gcp.secrets.get_sercret_by_uri` function.

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
    """
    secret = get_secret_by_name(host_project, secret_name, decode=True, **kwargs)
    return json.loads(secret)


def get_secret_by_name(host_project, secret_name, **kwargs):
    """
    Gets a secret from GCP and returns it either as decoded
    utf-8 or raw bytes (depending on `decode` parameter).
    Executing account must have (at least) secret version
    accessor permissions on the secret.
    Any extra arguments (``kwargs``) are passed to the :func:`~bibtutils.gcp.secrets.get_sercret_by_uri` function.

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
    """
    secret_uri = f"projects/{host_project}/secrets/{secret_name}/versions/latest"
    return get_secret_by_uri(secret_uri, **kwargs)


def get_secret_by_uri(secret_uri, decode=True, credentials=None, timeout=None):
    """
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

    :type credentials: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :param credentials: the credentials object to use when making the API call, if not to
        use the account running the function for authentication.

    :type timeout: :py:class:`float`
    :param timeout: request timeout may be specified if desired.

    :rtype: :py:class:`bytes` OR :py:class:`str`
    :returns: the secret data.
    """
    _LOGGER.info(f"Getting secret: {secret_uri}")
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    secret = client.access_secret_version(
        request={"name": secret_uri}, timeout=timeout
    ).payload.data
    if decode:
        return secret.decode("utf-8")
    return secret
