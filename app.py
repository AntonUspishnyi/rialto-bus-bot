#!/usr/bin/env python3

from aws_cdk import core as cdk
from rialto_bus_bot.rialto_bus_bot_stack import RialtoBusBotStack


app = cdk.App()
RialtoBusBotStack(app, "rialto-bus-bot", env={"region": "eu-north-1"})

app.synth()
