import json
import os
import logging
from pygelf import GelfUdpHandler
from bot import run

logging.getLogger().addHandler(GelfUdpHandler(
    host=os.environ['GRAYLOG_URL'],
    port=int(os.environ['GRAYLOG_PORT']),
    include_extra_fields=True,
    tag=os.environ['GRAYLOG_TAG']
))


def lambda_handler(event, context):
    try:
        logging.warning(f'Incoming body for DEBUG:\n{event}') # tmp for debug
        return {
            'statusCode': 200,
            'body': run(json.loads(event['body']))
        }

    except Exception as e:
        logging.error(f'Error: {e}\nEvent body: {event}', exc_info=True)

        return {
            'statusCode': 500,
            'body': 'Something went wrong'
        }
