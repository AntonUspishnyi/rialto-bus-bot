#!/usr/bin/env python3

import datetime

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
    "last_deploy_at": datetime.datetime.utcnow().isoformat(),
}
stack_env = {"region": "eu-north-1"}

app = cdk.App()
RialtoBusBotStack(app, stack_name, tags=stack_tags, env=stack_env)

app.synth()
