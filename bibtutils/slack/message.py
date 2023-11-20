"""
bibtutils.slack.message
~~~~~~~~~~~~~~~~~~~~~~~

Enables sending messages to Slack.

"""
import logging

import requests

_LOGGER = logging.getLogger(__name__)

SLACK_MAX_TEXT_LENGTH = 3000 - 35


def send_message(webhook, title, text=None, color=None, blocks=None):
    """Sends a message to Slack.

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
    """
    if not color:
        color = "#000000"
    if text:
        if len(text) > SLACK_MAX_TEXT_LENGTH:
            text = text[:SLACK_MAX_TEXT_LENGTH] + "\n..."
        msg = {
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": title}}],
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn", "text": text}}
                    ],
                }
            ],
        }
    elif blocks:
        msg = {
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": title}}],
            "attachments": [
                {
                    "color": color,
                    "blocks": [],
                }
            ],
        }
        for block in blocks:
            if len(block) > SLACK_MAX_TEXT_LENGTH:
                block = block[:SLACK_MAX_TEXT_LENGTH] + "\n..."
            msg["attachments"][0]["blocks"].append(
                {"type": "section", "text": {"type": "mrkdwn", "text": block}}
            )
    else:
        raise Exception("Either text or blocks must be passed.")
    r = requests.post(webhook, json=msg)
    r.raise_for_status()
    return
