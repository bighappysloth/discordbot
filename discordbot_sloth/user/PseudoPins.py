import logging


from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *

logger = logging.getLogger(__name__)


__PINS_FOLDER_NAME__ = "pins"
__PINS_FOLDER_PATH__ = __DATA_PATH__ / __PINS_FOLDER_NAME__
__PINS_RECENTS_CAPACITY__ = 50

check_dir(__PINS_FOLDER_PATH__)


def message_identifier(channel_id, message_id):
    return f"{channel_id},{message_id}"


if __name__ == "__main__":
    pass
