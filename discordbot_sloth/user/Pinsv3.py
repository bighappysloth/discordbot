import logging

from discordbot_sloth.user.AbstractPanel import AbstractPanel
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.user.PseudoPins import message_identifier
from discordbot_sloth.user.State import State

logger = logging.getLogger(__name__)


class PinPanel(AbstractPanel):
    def __init__(
        self,
        channel_id,
        message_id,
        user,
        cache=None,
        created_date=current_time(),
        created_unix_date=epoch_delta_milliseconds(),
    ):

        # These two fields define the partial that we can refresh()
        self.channel_id = channel_id
        self.message_id = message_id

        # The date when the user created this pin
        # When we init a new pin, leave the two fields blank in the constructor.
        # If loading from memory we do 'load'

        # The Pin that is the AbstractPanel should be different than the 'pins' saved within user_state.json.
        # One handles the interactions, the other is the cache.
        self.created_date = created_date
        self.created_unix_date = created_unix_date

        self.cache = cache  # Cached Message

    async def on_reaction_add(self, emoji, bot):
        pass

    async def on_reaction_remove(self, emoji, bot):
        if emoji == STAR_EMOJI:
            self.dead = True
            identifier = message_identifier(
                channel_id=self.channel_id, message_id=self.message_id
            )

            s = bot.states.get(self.user)
            if s is None:
                bot.states[self.user] = State(self.user, bot)
                s = bot.states[self.user]
            try:
                s.state.pop(identifier)
            except KeyError:
                logger.warning(f"Unable to remove pin {identifier}")

    async def on_edit(self, after, bot):
        pass

    def __iter__(self):
        out = {
            "type": "pinned_message" if not self.dead else "dead",
            "memory": {"user": self.user},
        }
