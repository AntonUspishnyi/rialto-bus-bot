#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from dotenv import load_dotenv
from rialto_bus_bot.rialto_bus_bot_stack import RialtoBusBotStack

# Load env from .env to simplify local development
load_dotenv()

# Stack parameters
stack_name = "rialto-bus-bot"
description = os.getenv("WORKFLOW_URL") or "No url specified"
stack_tags = {"project": stack_name, "cdk": "true", "CI": os.getenv("CI", "false")}

app = cdk.App()
RialtoBusBotStack(app, stack_name, description=description, tags=stack_tags)

app.synth()
