#!/usr/bin/env python3

from aws_cdk import core as cdk
from dotenv import load_dotenv
from rialto_bus_bot.rialto_bus_bot_stack import RialtoBusBotStack

# Load env from .env to simplify local development
load_dotenv()

# Stack parameters
stack_name = "rialto-bus-bot"
stack_tags = {
    "project": stack_name,
    "cdk": "true",
}

app = cdk.App()
RialtoBusBotStack(app, stack_name, tags=stack_tags)

app.synth()
