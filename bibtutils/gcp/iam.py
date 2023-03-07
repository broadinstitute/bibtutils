import logging

from google.api_core import exceptions as google_exceptions
from google.cloud import iam_credentials
from google.oauth2 import credentials

_LOGGER = logging.getLogger(__name__)


def get_access_token(acct, scopes=["https://www.googleapis.com/auth/cloud-platform"]):
    """
    Generates an access token for a target service account which may be used
    to impersonate that service account in API calls. Requires the calling account
    have the "Service Account Token Creator" role on the target account.

    .. code:: python

        from bibtutils.gcp import iam
        from google.oauth2 import credentials
        def main(event, context):
            token = iam.get_access_token(
                acct="myserviceaccount@myproject.iam.gserviceaccount.com"
            )
            api_creds = credentials.Credentials(token=token)
            storage_client = storage.Client(credentials=api_creds)
            storage_client.get_bucket("mybucket")

    :type acct: :py:class:`str`
    :param acct: the email address of the account to impersonate.

    :type scopes: :py:class:`list`
    :param scopes: the scopes to request for the token. by default, will be set
        to ``["https://www.googleapis.com/auth/cloud-platform"]`` which
        should be sufficient for most uses cases.

    :rtype: :py:class:`str`
    :returns: an access token with can be used to generate credentials for Google APIs.
    """
    # Create credentials for Logging API at the org level
    _LOGGER.info(f"Getting access token for account: [{acct}] with scope: [{scopes}]")
    client = iam_credentials.IAMCredentialsClient()
    try:
        resp = client.generate_access_token(
            name=acct,
            scope=scopes,
        )
    except google_exceptions.PermissionDenied as e:
        _LOGGER.critical(
            "Permission denied while attempting to create access token. "
            'Ensure that the account running this function has the "Service Account Token Creator" '
            f"role on the target account ({acct})."
        )
        raise e

    _LOGGER.info("Returning access token.")
    return resp.access_token


def get_credentials(acct, scopes=["https://www.googleapis.com/auth/cloud-platform"]):
    """
    Generates a credentials object for a target service account which may be used
    to impersonate that service account in API calls. Requires the calling account
    have the "Service Account Token Creator" role on the target account. This version
    takes care of credentials object creation for you.

    .. code:: python

        from bibtutils.gcp import iam
        from google.oauth2 import credentials
        def main(event, context):
            api_creds = iam.get_credentials(
                acct="myserviceaccount@myproject.iam.gserviceaccount.com"
            )
            storage_client = storage.Client(credentials=api_creds)
            storage_client.get_bucket("mybucket")

    :type acct: :py:class:`str`
    :param acct: the email address of the account to impersonate.

    :type scopes: :py:class:`list`
    :param scopes: the scopes to request for the token. by default, will be set
        to ``["https://www.googleapis.com/auth/cloud-platform"]`` which
        should be sufficient for most uses cases.

    :rtype: :py:class:`google_auth:google.oauth2.credentials.Credentials`
    :returns: a credentials object with can be used for authentication with Google APIs.
    """
    access_token = get_access_token(acct=acct, scopes=scopes)

    _LOGGER.info("Generating and returning credentials object.")
    return credentials.Credentials(token=access_token)
