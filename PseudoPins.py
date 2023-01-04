import discord
from pathlib import Path
import logging

from module_configs.matplotlib_args import HelperString
import bot_helpers

# PseudoPins

__PINS_FOLDER_PATH__ = Path('./pins')


#Addressing:
#Guild.Channel.Message
def channel_identifier(ctx):

    if isinstance(ctx.channel,discord.DMChannel):
        name = f'dm_{ctx.channel.recipient}'
        id = ctx.channel.id
        result = {
            'name': f'dm_{ctx.channel.recipient.id}',
            'title': f'dm_{ctx.channel.recipient.name}',
            'id': str(ctx.channel.recipient.id),
            'channel_id': str(ctx.channel.id),
            'type': 'dm'
        }
    elif isinstance(ctx.channel, (discord.TextChannel,
    discord.GroupChannel, discord.WelcomeChannel)):
        result = {\
            'name': f'channel_{ctx.channel.id}',
            'title': f'channel_{ctx.channel.name}',

            'id': str(ctx.channel.id),
            'guild_id': str(ctx.guild.id),
            'guild_title': str(ctx.guild.name),

            'type': 'channel',
        }
    elif isinstance(ctx.channel, discord.Thread):
        result={\
            'name': f'thread_{ctx.channel.id}',
            'title': f'channel_{ctx.channel.name}',
            
            'id': str(ctx.channel.id),
            
            'message_id': str(ctx.message.id),
            'channel_id': str(ctx.channel.id),
            'guild_id': str(ctx.guild.id),
            'guild_title': str(ctx.guild.name),

            'parent_channel': ctx.channel.parent.id,
            'type': 'thread',
        }
    if ctx.message.reference:
        # print(f'Reference Detected: {ctx.message.reference}')

        result['reference']={\
        'referenced_id': ctx.message.reference.message_id,
        'referenced_message': ctx.message.reference.cached_message,
        }
    return result

def message_identifiers(ctx):
    return {\
        'message_id': str(ctx.message.id),
        'channel_id': str(ctx.channel.id)
    }

async def fetch_message(bot, channel_id, message_id):
    c = bot.get_channel(int(channel_id))
    m = await c.fetch_message(int(message_id))
    return m

class PseudoPin:

    async def __init__(self, 
                        channel_id, 
                        user_id, 
                        message_id, 
                        date, 
                        unix_date, 
                        bot):
        self.channel_id = channel_id
        self.user_id = user_id
        self.message_id = message_id
        self.date = date
        self.unix_date = unix_date
        x = self.refresh(bot)
        if x['status']=='failure':
            logging.debug(f'PinError: {x.msg}')
            self.cache = x
    
    
    async def refresh(self, bot):  
        """
        Attempts to fetch message on refresh. Updates self.cache if success, else returns a failure message.
        """
        try:
            m = fetch_message(bot, self.channel_id, self.message_id)
        except Exception as E:
            return {\
                'status': 'failure',
                'msg': HelperString.list_printer([str(z) for z in E.args]),
                'updated': bot_helpers.current_time(),
                'updated_unix': bot_helpers.epoch_delta_milliseconds
            }
        else:
            self.cache = result = {\
                'status': 'success',
                'msg' : m,
                'updated': bot_helpers.current_time(),
                'updated_unix': bot_helpers.epoch_delta_milliseconds
            }
            return result

    async def get_latest(self, bot):
        """
        Returns 'best known' message, use with get_latest(bot)['msg']
        """
        x = self.refresh(bot)
        if x['status']=='failure':
            return self.cache
        else:
            return x

    
    async def __iter__(self):
        """
        Produces Dictionary with dict(x)
        """
        attrs = ['channel_id', 'user_id', 'message_id', 'date', 'unix_date', 'cached_message']
        
        vals = [self.channel_id, self.user_id, self.message_id, self.date, self.unix_date, self.cache]
        
        for z in zip(attrs,vals): yield z

        

class UserPins:

    class Pin:

        def __init__(self, channel_id, user_id, message_id, date, cached_message, unix_date):
            self.channel_id = channel_id
            self.user_id = user_id
            self.message_id = message_id
            self.date = date
            self.cached_message = cached_message
            self.unix_date = unix_date

        async def refresh(self, bot): # require passing an instance of the bot
            m = await fetch_message(bot, self.channel_id, self.message_id)
            if m != self.cached_message: cached_message = m
            return m


    def __init__(self, user):
        self.user = user
        # Load all pins into memory

    
    def add_pin(self, pinned_message):
        pass
    


def user_pins_path(user):
    return __PINS_FOLDER_PATH__/(user + r'_pins.json')
