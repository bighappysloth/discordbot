import json
import logging


import discord

from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.user.PseudoPins import message_identifier

logger = logging.getLogger(__name__)


TRACKED_TYPES = {\
    'show_pins_dialogue': 0,
    'latex_image': 1,
}


# Implementing tracked messages.

class TrackedMessage(discord.PartialMessage):
    
    def __init__ (self, channel, id, type, memory=None):
        # Notice we have to pass in a non-null channel.
        # This is prone to some NoneType errors. The client should check if the channel is valid or not.
        super(channel=channel, id = int(id))
        
        self.memory=memory
        self.created_date = current_time()
        self.created_unix_date = epoch_delta_milliseconds()
        self.type = type    
    
    def __iter__(self):
        attrs = [
        "channel_id",
        "message_id",
        "created_date",
        "created_unix_date",
        "memory",
        "type"
        ]

        vals = [
            self.channel_id,
            self.message_id,
            self.created_date,
            self.created_unix_date,
            self.memory,
            self.type,
        ]
        for z in zip(attrs,vals): yield z
    
    def identifier(self):
        return message_identifier(channel_id = self.channel_id,
                           message_id=self.message_id)
    
class TrackedShowPinsMessage(TrackedMessage):
    
    def __init__(self, user):
        pass
    
            
        