import discord

from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.helpers.TimeFormat import __TIME_FORMAT__
from discordbot_sloth.user.PseudoPins import message_identifier


class StarredMessage:
    def __init__(
        self,
        channel_id,
        message_id,
        created_date=None,
        created_unix_date=None,
        cache=None,
    ):

        self.channel_id = channel_id
        self.message_id = message_id
        self.cache = cache

        self.created_date = created_date if created_date is not None else current_time()
        self.created_unix_date = created_unix_date if created_unix_date is not None else epoch()
        #print(f'Pin: {self.created_date}')
        print(f'Pin: {self.created_unix_date}')

    async def refresh(self, bot):

        channel = bot.get_channel(self.channel_id)
        if not channel:
            channel = await bot.fetch_channel(self.channel_id)  # uncached

        try:
            partial = discord.PartialMessage(channel=channel, id=int(self.message_id))
            full_message = await partial.fetch()
            logger.debug("Partial Message: %s" % full_message.content)

            attachments_url = (
                []
                if not full_message.attachments
                else [A.url for A in full_message.attachments]
            )

            if attachments_url:
                logger.debug(
                    "List of attachments URL: \n%s" % list_printer(attachments_url)
                )

        except Exception as E:

            if self.cache is None:
                if self.cache["status"] != "success":
                    self.cache = {
                        "status": "failure",
                        "msg": list_printer([str(z) for z in E.args]),
                        "updated": current_time(),
                        "updated_unix": epoch(),
                    }

            logger.warning(f"Problem occured with refreshing pin: {self.cache['msg']}")

        else:
            # Successful
            identifier = message_identifier(self.channel_id, self.message_id)

            logger.debug(f"Success in Refreshing Pin: {identifier}")

            self.cache = {
                "status": "success",
                "author": full_message.author.name,
                "content": full_message.content,
                "attachments_url": attachments_url,
                "date_sent": fmt_date(full_message.created_at),
                "date_sent_unix": "",
                "updated": current_time(),
                "updated_unix": epoch(),
            }

    def __iter__(self):

        out = {
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "created_date": self.created_date,
            "created_unix_date": self.created_unix_date,
            "cache": self.cache,
        }

        for (k, v) in out.items():
            yield (k, v)

    def __str__(self):
        """attempts to reconstruct message from cache only.

        Returns:
            string: string
        """
        try:
            message_content = self.cache["content"]
            message_attachments_url = self.cache["attachments_url"]
            message_author = self.cache["author"]  # author name and not id
            message_date = self.cache["date_sent"]  # not the pin date
            
            x = "Sent {0} by {1}".format(
                fmt_date(datetime.strptime(message_date, __TIME_FORMAT__)), 
                message_author
            )
            x = (
                x + "\n" + "> Pinned Message: " + message_content
                if message_content
                else x
            )

            A = (
                "\n\n" + list_printer(message_attachments_url)
                if message_attachments_url
                else ""
            )
            x = x + A
            return x
        except Exception as E:
            s = "Error: " + list_printer([z for z in E.args])
            logger.warning(s)
            return s

    def __le__(self, other):
        return int(self.created_unix_date) <= int(other.created_unix_date)

    def __lt__(self, other):
        return int(self.created_unix_date) < int(other.created_unix_date)

    def __ge__(self, other):
        return int(self.created_unix_date) >= int(other.created_unix_date)

    def __gt__(self, other):
        return int(self.created_unix_date) > int(other.created_unix_date)
