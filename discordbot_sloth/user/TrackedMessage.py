import json
import logging

import discord

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.user.PseudoPins import message_identifier

logger = logging.getLogger(__name__)


# Implementing tracked messages.


class TrackedMessage(discord.PartialMessage):
    def __init__(self, channel, id, type, memory=None):
        # Notice we have to pass in a non-null channel.
        # This is prone to some NoneType errors. The client should check if the channel is valid or not.
        super(channel=channel, id=int(id))

        self.memory = memory
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
            "type",
        ]

        vals = [
            self.channel_id,
            self.message_id,
            self.created_date,
            self.created_unix_date,
            self.memory,
            self.type,
        ]
        for z in zip(attrs, vals):
            yield z

    def identifier(self):
        return message_identifier(
            channel_id=self.channel_id, message_id=self.message_id
        )


condition_channel = lambda pin, channel_id: pin["channel_id"] == channel_id


class TrackedShowPinsMessage(TrackedMessage):

    # Always show 3 pins per page.

    async def build_pages(
        self, list_of_pins, author_name, ctx, condition=lambda a: True
    ):
        # Usage: x = await UserPins.get_pins(user)
        # This method should be able to return a TrackedMessage, not beloning to this object itself.

        # Filter and Sort.
        z = list_of_pins.copy()
        list_of_messages = list(filter(condition, z))
        list_of_messages.sort(key=lambda a: int(dict(a)["created_unix_date"]))

        if list_of_messages:

            numpages = int(list_of_messages / 3) + 1

            delimiters = {
                "start_firstpage": "{0} List of Pins for {1}\n",
                "start": "",
                "end": "\nPage {0}/{1}\n",
            }

            pages = []
            for i in range(1, numpages + 1):
                if i == 1:
                    x = delimiters["start_firstpage"].format(STAR_EMOJI, author_name)
                else:
                    x = delimiters["start"].format(STAR_EMOJI, author_name)
                x = (
                    x
                    + list_of_messages[3 * (i - 1), 3 * i]
                    + delimiters["end"].format(str(i), str(numpages))
                )
                pages.append(x)
            self.memory["pages"] = pages

            logger.debug(f"Built {numpages} pages.")
            temp = await ctx.reply(self.memory["pages"][0])

            await temp.add_reaction(PAGE_EMOJIS["prev_page"])
            await temp.add_reaction(PAGE_EMOJIS["next_page"])

            self.memory["current_page"] = 1
            self.memory["numpages"] = numpages
        else:
            pass


    async def on_nextpage(self, bot):
        # Should be able to edit.
        if self.memory["current_page"] + 1 in range(1, self.memory["num_pages"] + 1):
            self.memory["current_page"] = self.memory["current_page"] + 1
            channel = bot.get_channel(self.channel_id)
            if not channel:
                channel = await bot.fetch_channel(self.channel_id)
            try:
                partial = discord.PartialMessage(
                    chanel=channel, id=int(self.message_id)
                )
                partial.edit(content=self.memory["pages"][self.memory["current_page"]])
            except Exception as E:
                logger.warning("Exception: " + list_printer([str(z) for z in E.args]))


    async def on_previouspage(self, bot):
        if self.memory["current_page"] - 1 in range(1, self.memory["num_pages"] + 1):
            self.memory["current_page"] = self.memory["current_page"] - 1
            channel = bot.get_channel(self.channel_id)
            if not channel:
                channel = await bot.fetch_channel(self.channel_id)
            try:
                partial = discord.PartialMessage(
                    chanel=channel, id=int(self.message_id)
                )
                partial.edit(content=self.memory["pages"][self.memory["current_page"]])
            except Exception as E:
                logger.warning("Exception: " + list_printer([str(z) for z in E.args]))


"""
Brainstorming
Each user can open one window of each type. And for each window the reacitons are tracked.


Whenever a raw reaction from a non-bot is detected, 
-> check if it is a star emoji
    -> if star emoji, then go through pin logic.
-> else: check if the message identifier belongs to the reacting user's tracked messages
-> load the tracked message and perform the task.
"""
