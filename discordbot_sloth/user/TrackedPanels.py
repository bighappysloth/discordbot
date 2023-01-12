import discord

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.helpers.EmojiReactor import react_to_message
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.modules.latex_to_png import latex_to_png_converter
from discordbot_sloth.user.AbstractPanel import AbstractPanel
from discordbot_sloth.user.user_configuration import Configuration


class ParrotMessage(AbstractPanel):
    def __init__(self, channel_id, message_id, word=None):
        # describes the channel_id, and the message_id of the parrot (the bot's reply)

        self.channel_id = channel_id
        self.message_id = message_id
        self.word = word

    async def on_edit(self, after, bot):

        channel = bot.get_channel(self.channel_id)
        if not channel:
            channel = await bot.fetch_channel(self.channel_id)

        partial = discord.PartialMessage(channel=channel, id=int(self.message_id))

        try:
            await partial.edit(content=PARROT_EMOJI + ": " + after)
            print("Success Changing")
            self.word = after

        except Exception as E:
            return {
                "status": "failure",
                "msg": list_printer([str(z) for z in E.args]),
                "memory": {
                    "channel_id": self.channel_id,
                    "message_id": self.message_id,
                    "word": self.word,
                },
            }
        else:
            return {
                "status": "success",
                "msg": f"Edited -> {after}",
                "memory": {
                    "channel_id": self.channel_id,
                    "message_id": self.message_id,
                    "word": self.word,
                },
            }

    async def on_reaction_add(self, emoji, bot):
        pass

    async def on_reaction_remove(self, emoji, bot):
        pass

    def __iter__(self):
        out = {
            "type": "parrot_message",
            "memory": {
                "channel_id": self.channel_id,
                "message_id": self.message_id,
                "word": self.word,
            },
        }
        for k, v in out.items():
            yield (k, v)


class LatexImage(AbstractPanel):
    def __init__(self, channel_id, message_id, user):
        self.channel_id = channel_id
        self.message_id = message_id
        self.user = user

    async def on_reaction_add(self, emoji, bot):
        pass

    async def on_reaction_remove(self, emoji, bot):
        pass

    async def on_edit(self, after, bot):

        Config = Configuration(self.user)
        result = await latex_to_png_converter(
            after,
            DENSITY=int(Config.getEntry("png_dpi")["msg"]),
            tex_mode=Config.getEntry("latex_mode")["msg"],
            framing=Config.getEntry("framing")["msg"],
        )

        channel = bot.get_channel(self.channel_id)
        if not channel:
            channel = await bot.fetch_channel(self.channel_id)

        partial = discord.PartialMessage(channel=channel, id=int(self.message_id))

        full = await partial.fetch()

        formatting = {
            "success": r"**Success**",
            "compile_fail": r"**Error: ** ```{0}```",
            "png_fail": r"**PNG Error. Unrecoverable: ```{0}```**",
        }

        if result["status"] == "success":
            im_location = result["image_path"]
            with Path(im_location).open("rb") as fp:
                await full.edit(content=formatting["success"])
                await full.add_files(discord.FIle(fp, im_location))

        else:  # Either compilation or PNG error.

            if result.get("log:"):
                await full.edit(
                    content=formatting.format(result["log"])
                )  # replies with log

            if result.get("image_path"):  # compile error
                im_location = result["image_path"]
                if Path(im_location):
                    with Path(im_location).open("rb") as fp:
                        await full.add_files(discord.File(fp, im_location))
            else:  # png error
                logger.warning('PNG Failure: {result["msg"]}')
                await full.edit(content=formatting["png_fail"].format(result["msg"]))

        def __iter__(self):
            out = {
                "type": "latex_image",
                "memory": {
                    "channel_id": self.channel_id,
                    "message_id": self.message_id,
                    "user": self.user,
                },
            }
            for k, v in out.items():
                yield (k, v)


class ShowPinsPanel(AbstractPanel):
    
    
    @staticmethod
    def build_pages(
        list_of_pins,
        author_name,
        condition=lambda a: True,
        sort=lambda a: int(dict(a)["created_unix_date"]),
    ):
        z = list_of_pins.copy()
        list_of_messages = list(filter(condition, z))

        list_of_messages.sort(key=sort)
        pages = []
        
        A = [f"{i+1}) {list_of_messages[i]}" for i in range(0, len(list_of_messages))]
        print('A: \n')
        for z in A:
            print(z,end='======')
        if list_of_messages:
            numpages = int(len(A) / 3) + 1
            delimiters = {
                "start_firstpage": "{0} List of Pins for {1}\n",
                "start": "{0} List of Pins for {1}\n",
                "end": "\nPage {0}/{1}\n",
            }

            for i in range(1, numpages + 1):
                end = min(3*i, len(A))
                s = list_printer(A[3 * (i - 1): end])
                
                x = delimiters["start"].format(STAR_EMOJI, author_name) + \
                    s + \
                    delimiters["end"].format(str(i), str(numpages))
                pages.append(x)
                print(x)
        else:
            numpages = 1

            pages = [f"You have 0 pins. React with {STAR_EMOJI} to pin a message."]

        return pages

    def __init__(self, channel_id, message_id, pages, current_page):

        """Builds the required pages and saves to memory

        # Client should reply to command with a message like

        m = await ctx.reply('Fetching Pins...')

        # Then we can get message and channel id of the reply. Of which we will also track under the name of the user.

        message_id = m.id
        channel_id = m.channel.id
        temp = await UserPins.get_pins(u, bot)



        x = ShowPinsPanel(channel_id = channel_id,
        message_id = message_id,
        author_name=ctx.author.name,
        list_of_pins = temp['msg']
        )



        # Because on __init__ the current_page is set to 0.
        # Require the client to also use

        await x.on_reaction_add(emoji = NEXT_PAGE_EMOJI, bot)

        # To get the first page. Now to save it to the TrackedPanels
        # The identifier is the same as the TrackedPanel

        identifier = message_identifier(channel_id = channel_id,
        message_id = message_id)

        s.state[identifier] = dict(x)
        s.save()

        """
        # Build the pages first

        self.channel_id = channel_id
        self.message_id = message_id
        self.pages = pages
        self.current_page = current_page

    async def on_reaction_add(self, emoji, bot):

        numpages = len(self.pages)
        emojis = [PAGE_EMOJIS["prev_page"], PAGE_EMOJIS["next_page"]]
        
        
        # 1) Edit Message

        

        if emoji == PAGE_EMOJIS["next_page"]:
            if self.current_page + 1 in range(1, numpages + 1):
                self.current_page = self.current_page + 1
        elif emoji == PAGE_EMOJIS["prev_page"]:
            if self.current_page - 1 in range(1, numpages + 1):
                self.current_page = self.current_page - 1

        channel = bot.get_channel(self.channel_id)
        if not channel:
            channel = await bot.fetch_channel(self.channel_id)
        try:
            partial = discord.PartialMessage(channel=channel, id=int(self.message_id))
            await partial.edit(content=self.pages[self.current_page-1])
        except Exception as E:
            logger.warning("Exception : " + list_printer([str(z) for z in E.args]))

        # 2) Clear Reactions (if possible)
        try:
            await partial.clear_reactions()
        except Exception as E:
            pass

        # 3) Add Reactions
        for e in emojis:
            await react_to_message(bot, self.channel_id, self.message_id, e, "add")

    async def on_reaction_remove(self, emoji, bot):
        pass

    async def on_edit(self, after, bot):
        pass

    def __iter__(self):
        out = {
            "type": "pins_panel",
            "memory": {
                "channel_id": self.channel_id,
                "message_id": self.message_id,
                "pages": self.pages,
                "current_page": self.current_page,
            },
        }
        for (k, v) in out.items():
            yield (k, v)
