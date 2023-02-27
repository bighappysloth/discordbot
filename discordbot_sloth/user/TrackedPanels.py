import discord

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.helpers.EmojiReactor import react_to_message
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.modules.latex_to_png import latex_to_png_converter
from discordbot_sloth.user.AbstractPanel import AbstractPanel
from discordbot_sloth.user.user_configuration import Configuration


class PinPanel(AbstractPanel):
    """Class that monitors the removal of reactions for a Pin

        # The date when the user created this pin
        # When we init a new pin, leave the two fields blank in the constructor.


        # The Pin that is the AbstractPanel should be different than the 'pins' saved within user_state.json.

        # One handles the interactions, the other is the cache.
    Args:
        AbstractPanel (_type_): _description_
    """

    def __init__(
        self,
        channel_id,
        message_id,
        user,
        created_date=None,
        created_unix_date=None,
    ):

        # These two fields define the partial that we can refresh()
        self.channel_id = channel_id
        self.message_id = message_id

        self.created_date = created_date
        self.created_unix_date = created_unix_date
        self.user = user
        self.dead = False

    async def on_reaction_add(self, emoji, bot):
        pass

    async def on_reaction_remove(self, emoji, bot):
        # The removal should be handled by the main event loop.
        pass

    async def on_edit(self, after, bot):
        pass

    def __iter__(self):
        out = {
            "type": "pinned_message" if not self.dead else "dead",
            "memory": {"user": self.user},
        }

        temp = super().timestamp()

        for (k, v) in temp.items():
            out["memory"][k] = v

        for (k, v) in out.items():
            yield (k, v)


class ParrotMessage(AbstractPanel):
    def __init__(
        self,
        channel_id,
        message_id,
        word=None,
        created_date=None,
        created_unix_date=None,
    ):

        # describes the channel_id, and the message_id of the parrot (the bot's reply)

        super().__init__(created_date, created_unix_date)

        self.channel_id = channel_id
        self.message_id = message_id
        self.word = word
        self.dead = False # deprecated

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
        temp = super().timestamp()
        for (k, v) in temp.items():
            out["memory"][k] = v
        for (k, v) in out.items():
            yield (k, v)


class LatexImage(AbstractPanel):
    # This is tracking the user's latex input in the form of !t
    
    def __init__(
        self, channel_id, message_id, user, created_date=None, created_unix_date=None
    ):
        super().__init__(created_date, created_unix_date)
        self.channel_id = channel_id
        self.message_id = message_id
        self.user = user

        self.dead = False

    async def on_reaction_add(self, emoji, bot):
        pass

    async def on_reaction_remove(self, emoji, bot):
        pass

    async def on_edit(self, after, bot):
        
        
        after = after[2:] if after.startswith(r'!t') else after         # remember to strip the !t
        Config = Configuration(self.user)                               # Load Config
        

        channel = bot.get_channel(self.channel_id)
        if not channel:
            channel = await bot.fetch_channel(self.channel_id)

        partial = discord.PartialMessage(channel=channel, 
                                         id=int(self.message_id))

        full = await partial.fetch()

        formatting = {
            "success": r"**Success**",
            "compile_fail": r"**Error: ** ```{0}```",
            "png_fail": r"**PNG Error. Unrecoverable: ```{0}```**",
        }

        result = await latex_to_png_converter(
                    after,
                    DENSITY=int(Config.getEntry("png_dpi")["msg"]),
                    tex_mode=Config.getEntry("latex_mode")["msg"],
                    framing=Config.getEntry("framing")["msg"],
                )
        if result["status"] == "success":

            im_location = result["image_path"]
            with Path(im_location).open("rb") as fp:
                await full.edit(content=formatting["success"])
                
                full = await full.remove_attachments(*full.attachments)
                await full.add_files(discord.File(fp, str(im_location)))

        else:  # Either compilation or PNG error.

            if result.get("log:"):
                await full.edit(
                    content=formatting.format(result["log"])
                )  # replies with log

            if result.get("image_path"):  # compile error
                im_location = result["image_path"]
                if Path(im_location):
                    with Path(im_location).open("rb") as fp:
                        await full.add_files(discord.File(fp, str(im_location)))
            
            else:  # png error
                logger.warning(f'PNG Failure: {result["msg"]}')
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
        temp = super().timestamp()
        for (k, v) in temp.items():
            out["memory"][k] = v
        for (k, v) in out.items():
            yield (k, v)

        for k, v in out.items():
            yield (k, v)


class ShowPinsPanel(AbstractPanel):
    @staticmethod
    def build_pages(pins, author_name, condition=lambda a: True, oldest_first=False):
        print(pins)
        list_of_StarredMessages = list(filter(condition, pins))

        # Sorting by descending StarredMessage (created_unix_date).
        # if oldest_first, then use ascending order
        
        list_of_StarredMessages.sort(reverse = not oldest_first)
        pages = []

        A = [
            f"{i+1}) {list_of_StarredMessages[i]}\n"
            for i in range(0, len(list_of_StarredMessages))
        ]

        print("A: \n")
        for z in A:
            print(z, end="======")

        if A: # if len(A) != 0

            numpages = int((len(A)-1) / 3) + 1

            delimiters = {
                "start_firstpage": "{0} List of Pins for {1}\n",
                "start": "{0} List of Pins for {1}\n",
                "end": "\nPage {0}/{1}\n",
            }

            for i in range(1, numpages + 1):
                end = min(3 * i, len(A))
                s = list_printer(A[3 * (i - 1) : end])

                x = (
                    delimiters["start"].format(STAR_EMOJI, author_name)
                    + s
                    + delimiters["end"].format(str(i), str(numpages))
                )
                pages.append(x)
                print(x)
        else:
            numpages = 1

            pages = [f"You have 0 pins. React with {STAR_EMOJI} to pin a message."]

        return pages

    def __init__(
        self,
        channel_id,
        message_id,
        pages,
        current_page,
        created_date=None,
        created_unix_date=None,
    ):

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
        super().__init__(created_date, created_unix_date)

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
            await partial.edit(content=self.pages[self.current_page - 1])
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
        temp = super().timestamp()
        for (k, v) in temp.items():
            out["memory"][k] = v
        for (k, v) in out.items():
            yield (k, v)
