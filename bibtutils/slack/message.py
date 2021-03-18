'''
bibtutils.slack.message
~~~~~~~~~~~~~~~~~~~~~~~

Enables sending messages to Slack.

'''

import os
import json
import logging
import requests
import datetime

logging.getLogger(__name__).addHandler(logging.NullHandler())


def send_message(webhook, title, text, color):
    '''Sends an error message to Slack. Not necessarily indicative of a crash.

    .. code:: python
    
        from bibtutils.slack.message import send_message

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
    msg = {
        'blocks': [{
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': title
            }
        }],
        'attachments': [{
            'color': color,
            'blocks': [{
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': text
                }
            }]
        }]
    }
    r = requests.post(webhook, json=msg)
    r.raise_for_status()
    return
