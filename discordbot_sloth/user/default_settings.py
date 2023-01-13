from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
import json
import logging

logger = logging.getLogger(__name__)


__DEFAULT_USER__ = "default"  # name of the default user

print(f"DEFAULT_USER: {__DEFAULT_USER__}")
__CONFIG_FOLDER_NAME__ = r"user_settings"

__CONFIG_FOLDER_PATH__ = __DATA_PATH__ / __CONFIG_FOLDER_NAME__

__DEFAULT_CONFIG_PATH__ = __CONFIG_FOLDER_PATH__ / r"default_settings.json"

__COMMAND_DEFAULT_SETTINGS__ = "!defaults"


check_dir(__DEFAULT_CONFIG_PATH__)

# We assert defaults for now.
DEFAULT_CONFIG = {
    "latex_mode": "inline",
    "framing": "regular",
    "latex_preamble": "",
    "usage": 0,
    "last_used": None,
    "background": "white",  # unused
    "png_dpi": 2400,
    "plot_samples": 100,
    "plot_grid": True,
    "plot_xlimits": [0, 10],
    "matplotlib_settings": {
        "plot": {
            "color": "tab:orange",
            "linewidth": 2.5,
        },
        "legend": {
            "loc": "upper right",
        },
    },
    "xprint_settings": {
        "verb": True,
        "env": "regular",
        "latex_mode": "inline",
        "use_title": False,
    },
}

with __DEFAULT_CONFIG_PATH__.open("w+") as f:
    f.write(json.dumps(DEFAULT_CONFIG))
    logger.debug(f"Writing to {__DEFAULT_CONFIG_PATH__}...")
    f.close()

with __DEFAULT_CONFIG_PATH__.open("r") as f:
    j = json.loads(f.read())
    logger.debug(f"Printing Default Settings: {j},\ntype: {type(j)}")
    f.close()
