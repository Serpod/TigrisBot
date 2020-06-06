import re
import discord
from settings import *

def is_private(channel):
    return isinstance(channel, discord.abc.PrivateChannel)

def is_allowed(channel):
    return is_private(channel) or channel.name in ALLOWED_CHAN

def format_username(user_id, username='', l=0, in_tick=False):
    # It's difficult to align things when mentions cannot be monospaced
    # /!\ This doesn't really work
    res = "<@{}>".format(user_id)
    if in_tick:
        # Escape mention from tick
        res = '`' + res + '`'
    if username and l > len(username):
        left_pad = ' '*((l - len(username) - 1)//2)
        res = left_pad + res
        right_pad = ' '*(l - len(left_pad + username) - 1)
        res += right_pad

    return res

pattern_id = re.compile("<@!?(\d+)>")

