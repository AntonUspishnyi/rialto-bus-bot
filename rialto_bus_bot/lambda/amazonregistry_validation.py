"""
It's a dummy method to validate the ownership of the bot.
The reason is to get domain name in .bot zone.
https://www.amazonregistry.com
"""


def handler(event, context) -> dict:
    print(event["body"])
    return {"statusCode": 200, "body": "OK"}
