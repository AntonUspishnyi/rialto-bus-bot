from bot import run
import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': run(json.dumps(json.loads(event['body'])))
    }