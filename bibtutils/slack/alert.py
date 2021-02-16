import os
import json
import logging
import requests
import datetime

logging.getLogger(__name__).addHandler(logging.NullHandler())

def _get_cfname() -> str:
    '''
    Helper function to get the current cloud function name. References environment variables set by GCP (`K_SERVICE` for Python 3.8+, or `FUNCTION_NAME` for Python 3.7).
    If neither value is set, returns 'UNKNOWN'.

    Returns:
        str: the cloud function name.
    '''
    cfname = os.environ.get('K_SERVICE', default=None)
    # If not, check for older name (Python 3.7)
    if not cfname:
        cfname = os.environ.get('FUNCTION_NAME', default='UNKNOWN')
    return cfname

def send_cf_fail_alert(currenttime:datetime.datetime, eventtime:datetime.datetime, webhook:str, proj_envar='_GOOGLE_PROJECT') -> None:
    '''
    Sends a cloud function runtime failure alert to Slack. Automatically called by the `bibtutils.gcp.pubsub.process_trigger()` method if function retry threshold is exceeded.
    Will include an appropriately-timestamped link to the cloud function's logs in the Slack message.

    Args:
        currenttime (datetime.datetime): a datetime object representing the current time.
        eventtime (datetime.datetime): a datetime object representing the original triggering time.
        webhook (str): a slack webhook in the standard format: `https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}`
        proj_envar (str, optional): the environment variable to reference for current GCP project. Defaults to '_GOOGLE_PROJECT'.
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
    msg = {
        'blocks': [{
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f':exclamation: *Cloud Function Failed* :exclamation: @here'
            }
        }],
        'attachments': [{
            'color': '#ff0000',
            'blocks': [{
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'`{cfname}` exceeded its retry threshold in `{os.environ.get("_GOOGLE_PROJECT")}`\n'
                            f'See logs here: <{hyperlink}|Logs Explorer>'
                }
            }]
        }]
    }
    r = requests.post(webhook, json=msg)
    r.raise_for_status()
    return

def send_cf_error(message:str, webhook:str, proj_envar='_GOOGLE_PROJECT') -> None:
    '''
    Sends an error message to Slack. Not necessarily indicative of a crash.

    Args:
        message (str): a description of the error, included as an attachment in the Slack message.
        webhook (str): a slack webhook in the standard format: `https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}`
        proj_envar (str, optional): the environment variable to reference for current GCP project. Defaults to '_GOOGLE_PROJECT'.
    '''
    cfname = _get_cfname()
    msg = {
        'blocks': [{
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': ':exclamation: *Cloud Function Encountered Error* :exclamation: @here\n'
                        f'\t- *Project*: `{os.environ.get(proj_envar)}`\n\t- *Function*: `{cfname}`'
            }
        }],
        'attachments': [{
            'color': '#ff0000',
            'blocks': [{
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': message
                }
            }]
        }]
    }
    r = requests.post(webhook, json=msg)
    r.raise_for_status()
    return