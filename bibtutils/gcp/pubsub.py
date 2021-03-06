'''
bibtutils.gcp.pubsub
~~~~~~~~~~~~~~~~~~~~

Functionality making use of GCP's PubSubs.

See the official PubSub Python Client documentation here: `link <https://googleapis.dev/python/pubsub/latest/index.html>`_.

'''

from bibtutils.slack.alert import send_cf_fail_alert
from bibtutils.gcp.secrets import get_secret_by_uri
from google.cloud import pubsub_v1
import os
import json
import logging
import base64
from dateutil.parser import parse
from datetime import datetime, timezone

logging.getLogger(__name__).addHandler(logging.NullHandler())

def retrigger_self(payload, proj_envar='_GOOGLE_PROJECT', topic_envar='_TRIGGER_TOPIC'):
    '''
    Dispatches the next iteration of a PubSub-triggered Cloud Function.

    .. code:: python

        from bibtutils.gcp.pubsub import process_trigger, retrigger_self
        def main(event, context):
            payload = process_trigger(event, context=context)
            print(payload)
            retrigger_self('All work and no play makes Jack a dull boy')

    :type payload: :py:class:`dict` OR :py:class:`str`
    :param payload: the pubsub payload. can be either a ``dict`` or a ``str``. 
        will be converted to bytes before sending.

    :type proj_envar: :py:class:`str`
    :param proj_envar: (Optional) the environment variable to 
        reference for current GCP project. Defaults to ``'_GOOGLE_PROJECT'``.
    
    :type topic_envar: :py:class:`str`
    :param topic_envar: (Optional) the environment variable to 
        reference for the triggering pubsub topic. Defaults to ``'_TRIGGER_TOPIC'``.
    '''
    logging.info(f'Dispatching next worker.')
    topic = f'projects/{os.environ.get(proj_envar)}/topics/{os.environ.get(topic_envar)}'
    send_pubsub(topic, payload)
    return


def send_pubsub(topic_uri, payload):
    '''
    Publishes a pubsub message to the specified topic. Executing account 
    must have pubsub publisher permissions on the topic or in the project.

    .. code:: python

        from bibtutils.gcp.pubsub import process_trigger, send_pubsub
        def main(event, context):
            process_trigger(event)
            topic_uri = f'projects/{os.environ["GOOGLE_PROJECT"]}/topics/{os.environ["NEXT_TOPIC"]}'
            send_pubsub(
                topic=topic_uri,
                payload={'favorite color': 'blue'}
            )

    :type topic_uri: :py:class:`str`
    :param topic_uri: the topic on which to publish. 
        topic uri format: ``'projects/{project_name}/topics/{topic_name}'``

    :type payload: :py:class:`dict` OR :py:class:`str`
    :param payload: the pubsub payload. can be either a ``dict`` or a ``str``. 
        will be converted to bytes before sending.
    '''
    publisher = pubsub_v1.PublisherClient()
    logging.info(f'Payload: {payload}\nPubSub: {topic_uri}')
    # Convert to Bytes then publish message.
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    payload_bytes = payload.encode('utf-8')
    publisher.publish(topic=topic_uri, data=payload_bytes)
    logging.info('PubSub sent.')
    return


def process_trigger(context, event=None, timeout_secs=1800, 
        fail_alert_webhook_secret_uri='FAIL_ALERT_WEBHOOK_SECRET_URI'):
    '''Check timestamp of triggering event; catches infinite retry 
    loops on 'retry on fail' cloud functions. Its good practice to always call
    this function first in a Cloud Function.
    
    If the timeout has been exceeded, will attempt to alert via Slack after 
    fetching a webhook in Secret Manager whose name should be provided in the 
    environment variable specified in the function call. **It expects to find a 
    full secret URI in that environment variable, not just a secret name!**
    
    **If (and only if)** the triggering pubsub's event is also passed **and has a payload**, 
    it will be decoded as utf-8 and returned. Otherwise, this function returns ``None``.

    .. code-block:: python
    
        import json
        from bibtutil.gcp.pubsub import process_trigger
        def main(event, context):
            payload = process_trigger(context, event=event)
            if not payload:
                raise IOError('No payload in triggering pubsub!')
            
            payload = json.loads(payload)

    :type context: :class:`google.cloud.functions.Context`
    :param context: the triggering pubsub's context.

    :type event: :py:class:`dict`
    :param event: (Optional) the triggering pubsub's event. defaults to :py:class:`None`.
    
    :type timeout_secs: :py:class:`int`
    :param timeout_secs: (Optional) the number of seconds to consider as 
        the timeout threshold from the original trigger time. Defaults to 1800.
    
    :type fail_alert_webhook_secret_uri: :py:class:`str`
    :param fail_alert_webhook_secret_uri: (Optional) the name of the 
        environment variable from which to read the secret URI. Defaults 
        to ``'FAIL_ALERT_WEBHOOK_SECRET_URI'``. secret uri format in the 
        envar: ``'projects/{host_project}/secrets/{secret_name}/versions/latest'``.

    :rtype: :py:class:`str` OR :py:class:`None`
    :returns: the pubsub payload, if present.

    '''
    utctime = datetime.now(timezone.utc)
    eventtime = parse(context.timestamp)
    lapsed = utctime - eventtime
    lapsed = datetime.now(timezone.utc) - parse(context.timestamp)
    logging.info(f'Lapsed time since triggering event: {lapsed.total_seconds()}')
    if lapsed.total_seconds() > timeout_secs:
        logging.critical(
            f'Threshold of {timeout_secs} seconds exceeded by '
            f'{lapsed.total_seconds()-timeout_secs} seconds. Exiting.'
        )
        try:
            webhook = get_secret_by_uri(os.environ.get(fail_alert_webhook_secret_uri))
            try:
                send_cf_fail_alert(utctime, eventtime, webhook['hook'])
            except Exception as e:
                logging.error(f'Could not send fail alert to Slack: {type(e).__name__}{e}')
                pass
        except Exception as e:
            logging.error(f'Could not get the Slack alert webhook from envar: {fail_alert_webhook_secret_uri}. Did you set a value here? Exception: {type(e).__name__}:{e}')
            pass
        return

    if event != None and 'data' in event:
        return base64.b64decode(event['data']).decode('utf-8')
    
    return None
