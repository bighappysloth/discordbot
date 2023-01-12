import discord
from discordbot_sloth.helpers.RegexReplacer import *


async def react_to_message(bot, channel_id, message_id, emoji, action='toggle'):

    channel = bot.get_channel(channel_id)
    if not channel:
        channel = await bot.fetch_channel(channel_id)
    try:
        partial = discord.PartialMessage(channel=channel,
                                         id = int(message_id))
        if action=='add':
            await partial.add_reaction(emoji)
            msg = f'Added reaction {emoji}.'
        elif action=='remove':
            await partial.remove_reaction(emoji,bot.user)
            msg = f'Removed reaction {emoji}.'
        elif action=='toggle':
            full = await partial.fetch()
            if list(filter(lambda a: a.me and a.emoji == emoji, full.reactions)):
                await partial.remove_reaction(emoji,bot.user)
                msg = f'Removed reaction {emoji}.'
            else:
                await partial.add_reaction(emoji)
                msg = f'Added reaction {emoji}.'
        temp = {\
            'status': 'success',
            'msg': msg,
        }
        logger.debug(f"{temp['status']}: {temp['msg']}")
        return temp
    
    except KeyError:
        return {\
            'status': 'failure',
            'msg': f'bot_reactor Action {action} not found.',
        }
         
    except Exception as E:
        logger.warning('Reaction Exception Occured')
        return {\
            'status': 'failure',
            'msg': list_printer([str(z) for z in E.args])
        }
        
        