'''
bibtutils.slack.error
~~~~~~~~~~~~~~~~~~~~~

Enables sending alerts (crashes and other errors) to Slack.

'''

import os
import logging
import datetime
from bibtutils.slack.message import send_message

logging.getLogger(__name__).addHandler(logging.NullHandler())


def _get_cfname():
    '''Helper function to get the current cloud function name. 
    References environment variables set by GCP (``'K_SERVICE'`` for Python 3.8+, 
    or ``'FUNCTION_NAME'`` for Python 3.7). If neither value is set, 
    returns ``'UNKNOWN'``.

    :rtype: :py:class:`str`
    :returns: the cloud function name.
    '''
    cfname = os.environ.get('K_SERVICE', default=None)
    # If not, check for older name (Python 3.7)
    if not cfname:
        cfname = os.environ.get('FUNCTION_NAME', default='UNKNOWN (running locally?)')
    return cfname


def send_cf_fail_alert(currenttime, eventtime, webhook, proj_envar='_GOOGLE_PROJECT'):
    '''Sends a cloud function runtime failure alert to Slack. 
    Automatically called by the :func:`~bibtutils.gcp.pubsub.process_trigger` 
    method if function retry threshold is exceeded. Will include an 
    appropriately-timestamped link to the cloud function's 
    logs in the Slack message.

    :type currenttime: :class:`datetime.datetime`
    :param currenttime: a datetime object representing the current time.

    :type eventtime: :class:`datetime.datetime`
    :param eventtime: a datetime object representing the 
        original triggering time.

    :type webhook: :py:class:`str`
    :param webhook: a slack webhook in the standard format: 
        ``'https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}'``
    
    :type proj_envar: :py:class:`str`
    :param proj_envar: (Optional) the environment variable to 
        reference for current GCP project. Defaults to ``'_GOOGLE_PROJECT'``.
    '''
    ctimestamp = currenttime.strftime('%Y%m%dT%H%M%SZ')
    etimestamp = eventtime.strftime('%Y%m%dT%H%M%SZ')
    cfname = _get_cfname()
    hyperlink = (
        'https://console.cloud.google.com/logs/query;query='
        'resource.type%3D%22cloud_function%22%0A'
        f'resource.labels.function_name%3D%22{cfname}%22;'
        f'timeRange={etimestamp}%2F{ctimestamp}'
        f'?project={os.environ.get("_GOOGLE_PROJECT")}'
    )
    title = ':exclamation: *Cloud Function Failed* :exclamation: @here'
    text = (
        f'`{cfname}` exceeded its retry threshold in '
        f'`{os.environ.get("_GOOGLE_PROJECT")}`\n'
        f'See logs here: <{hyperlink}|Logs Explorer>'
    )
    color = '#ff0000'
    send_message(webhook, title, text, color)
    return


def send_cf_error(message, webhook, proj_envar='_GOOGLE_PROJECT'):
    '''Sends an error message to Slack. Not necessarily indicative of a crash.

    .. code:: python
    
        from bibtutils.slack.error import send_cf_error
        try:
            raise IOError('Invalid input!')
        except IOError as e:
            send_cf_error(
                f'Exception raised! {type(e).__name__} : {e}',
                'https://hooks.slack.com/services/1234/1234/1234'
            )
            pass

    :type message: :py:class:`str`
    :param message: a description of the error, included as an 
        attachment in the Slack message.

    :type webhook: :py:class:`str`
    :param webhook: a slack webhook in the standard format: 
        ``'https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}'``
    
    :type proj_envar: :py:class:`str`
    :param proj_envar: (Optional) the environment variable to 
        reference for current GCP project. Defaults to ``'_GOOGLE_PROJECT'``.
    '''
    cfname = _get_cfname()
    title = (
        ':exclamation: *Cloud Function Encountered Error* :exclamation: @here\n'
        f'\t- *Project*: `{os.environ.get(proj_envar)}`\n\t- *Function*: `{cfname}`'
    )
    text = message
    color = '#ff0000'
    send_message(webhook, title, text, color)
    return