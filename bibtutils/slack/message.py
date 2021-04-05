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
    '''Sends a message to Slack.

    .. code:: python
    
        from bibtutils.slack.message import send_message
        ...

    :type webhook: :py:class:`str`
    :param webhook: a slack webhook in the standard format: 
        ``'https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}'``

    :type title: :py:class:`str`
    :param title: the title of the message. This will appear above the attachment. 
        Can be Slack-compatible markdown.
    
    :type text: :py:class:`str`
    :param text: the text to be included in the attachment. 
        Can be Slack-compatible markdown.
    
    :type color: :py:class:`str`
    :param color: the color to use for the Slack attachment border.
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
