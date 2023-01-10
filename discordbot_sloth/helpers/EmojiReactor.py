import discord
from discordbot_sloth.helpers.RegexReplacer import *


async def react_to_message(bot, channel_id, message_id, emoji, action='toggle'):

    perform = {\
        
        'add': lambda x,e: x.add_reaction(e),
        'remove': lambda x,e: x.remove_reaction(e),
        
        }

    channel = bot.get_channel(channel_id)
    if not channel:
        channel = await bot.fetch_channel(channel_id)
    try:
        partial = discord.PartialMessage(channel=channel,
                                         id = int(message_id))
        the_action = action
        if action=='toggle':
            full = await partial.fetch()
            if list(filter(lambda a: a.me and a.emoji == emoji, full.reactions)):
                the_action = 'remove'
            else:
                the_action = 'add'
        perform[the_action](partial, emoji)
    
    except KeyError:
        return {\
            'status': 'failure',
            'msg': f'bot_reactor Action {action} not found.',
        }
        
            
            
    except Exception as E:
        return {\
            'status': 'failure',
            'msg': list_printer([str(z) for z in E.args])
        }
        
        