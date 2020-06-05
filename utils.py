import re
import discord
from settings import *

def is_private(channel):
    return isinstance(channel, discord.abc.PrivateChannel)

def is_allowed(channel):
    return is_private(channel) or channel.name in ALLOWED_CHAN

pattern_id = re.compile("<@!?(\d+)>")

