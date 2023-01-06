import json
import logging

import discord

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *

logger = logging.getLogger(__name__)
# PseudoPins

__PINS_FOLDER_NAME__ = 'pins'
__PINS_FOLDER_PATH__ = __DATA_PATH__/__PINS_FOLDER_NAME__

check_dir(__PINS_FOLDER_PATH__)

# Addressing:
# Guild.Channel.Message


def channel_identifier(ctx):
    """
    This function does not do anything at the moment.
    We can merge this function to support Threads and DMs later.
    """

    if isinstance(ctx.channel, discord.DMChannel):
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
        result = {
            'name': f'channel_{ctx.channel.id}',
            'title': f'channel_{ctx.channel.name}',

            'id': str(ctx.channel.id),
            'guild_id': str(ctx.guild.id),
            'guild_title': str(ctx.guild.name),

            'type': 'channel',
        }
    elif isinstance(ctx.channel, discord.Thread):
        result = {
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

        result['reference'] = {
            'referenced_id': ctx.message.reference.message_id,
            'referenced_message': ctx.message.reference.cached_message,
        }
    return result


def message_identifiers(ctx):
    return {
        'message_id': str(ctx.message.id),
        'channel_id': str(ctx.channel.id)
    }


async def fetch_message(bot, channel_id, message_id):
    c = bot.get_channel(int(channel_id))
    m = await c.fetch_message(int(message_id))
    return m


class Pin:  # takes in a message

    def __init__(self,
                 channel_id,
                 message_id,
                 date,
                 unix_date,
                 cache=None):

        self.channel_id = channel_id
        self.message_id = message_id
        self.date = date
        self.unix_date = unix_date
        self.cache = cache

    async def refresh(self, bot):
        """
        Attempts to fetch message on refresh. Updates self.cache if success, else returns a failure message.
        """
        try:
            m = await fetch_message(bot, self.channel_id, self.message_id)
            msg = m.content
            if m.attachments:
                msg = msg + '\nAttachments: \n' + \
                    RegexReplacer.listprinter(m.attachments)

        except Exception as E:
            temp = {
                'status': 'failure',
                'msg': RegexReplacer.list_printer([str(z) for z in E.args]),
                'updated': current_time(),
                'updated_unix': epoch_delta_milliseconds()
            }

            # if no backup
            if (not self.cache) or (self.cache['status'] != 'success'):
                self.cache = temp
            logging.debug(f'Refresh PinError: {temp}')
            return temp

        else:
            self.cache = result = {
                'status': 'success',
                'msg': msg,
                'updated': current_time(),
                'updated_unix': epoch_delta_milliseconds()
            }
            logging.debug(f'Refreshed Pin: {m}')
            return result

    async def get_latest(self, bot):
        """
        Returns 'best known' message, use with get_latest(bot)['msg']
        """
        x = self.refresh(bot)
        if x['status'] == 'failure':
            return self.cache
        else:
            return x

    def __iter__(self):
        """
        Produces Dictionary with dict(x)
        """
        attrs = ['channel_id',
                 'message_id',
                 'date',
                 'unix_date',
                 'cache']

        vals = [self.channel_id,
                self.message_id,
                self.date,
                self.unix_date,
                self.cache]

        for z in zip(attrs, vals):
            yield z


class UserPins:

    @staticmethod
    async def add_pin(user, payload, bot):

        x = Pin(**payload)  # message to add to user's list of pins
        logger.debug('Adding Pin.')
        await x.refresh(bot)  # refresh first to get cache

        x = dict(x)

        # logger.debug(f'x: {x}')
        display_name = bot.get_user(int(user)).name,

        p = user_pins_path(user)
        try:
            with p.open('r') as fp:
                j = json.loads(fp.read())  # returns dictionary
                fp.close()

                with p.open('w') as fw:
                    try:
                        j['pins'].append(x)
                    except KeyError:
                        j['pins'] = []
                        j['pins'].append(x)
                        j['user'] = str(user)
                        j['display_name'] = str(display_name)
                    fw.write(json.dumps(j, sort_keys=True, indent=4))
                    fw.close()

                    return {
                        'status': 'success',
                        'msg': f'Added Pin: {x}'
                    }

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            j = {
                'user': str(user),
                'display_name': str(display_name),
                'pins': [x],
            }
            try:
                with p.open('w') as fw:
                    z = json.dumps(j, sort_keys=True, indent=4)
                    fw.write(z)
                    fw.close()

                    return {
                        'status': 'success',
                        'msg': f'Added Pin: {x}'
                    }
            except Exception as E:
                return {
                    'status': 'failure',
                    'msg': RegexReplacer.list_printer([str(z) for z in E.args])
                }

    @staticmethod
    async def get_pins(user, bot):
        # Need to create Pin objects from each JSON dictionary.
        # Instance of Pin Object does not require 'cache' key-val pair in the json dump.
        pins_path = user_pins_path(user)
        try:
            with pins_path.open('r') as fp:
                x = json.loads(fp.read())
                pinlist = [Pin(**z) for z in x['pins']]
                for z in pinlist:
                    z.refresh(bot)

                return [dict(z) for z in pinlist]

        except KeyError:
            return None
        except FileNotFoundError:
            return None
        except json.decoder.JSONDecodeError:  # empty
            return {
                'status': 'success',
                'msg': []
            }


def user_pins_path(user):
    return __PINS_FOLDER_PATH__/(user + r'_pins.json')
