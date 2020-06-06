import re
import discord
from settings import *

pattern_id = re.compile("<@!?(\d+)>")

def is_private(channel):
    return isinstance(channel, discord.abc.PrivateChannel)

def is_allowed(channel):
    return is_private(channel) or channel.name in ALLOWED_CHAN

def mention(user_id):
    return "<@{}>".format(user_id)

def get_user_id(m):
    match = pattern_id.match(m)
    if match is None:
        return None

    user_id = int(match.group(1))
    return user_id
