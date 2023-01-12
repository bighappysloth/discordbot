import json
import logging
import os

import discord

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


class UserPins:
    

    @staticmethod
    def user_pins_path(user):
        return __PINS_FOLDER_PATH__ / (user + r"_pins.json")

    @staticmethod
    async def restore_pins(user):
        try:
            # must fix this command
            if UserPins.user_pins_path(user):
                os.remove(UserPins.user_pins_path(user))
        except FileNotFoundError:
            return {"status": "success", "msg": f"Restored {user}'s pins."}
        except Exception as E:
            return {"status": "failure", "msg": list_printer([str(z) for z in E.args])}
        else:
            return {"status": "success", "msg": f"Restored {user}'s pins."}

    @staticmethod
    async def add_pin(user, payload, bot):

        w = UserPins.newPin(**payload)  # message to add to user's list of pins
        display_name = bot.get_user(int(user)).name
        identifier = message_identifier(**payload)

        logger.debug(f"Adding Pin: {identifier}")

        p = UserPins.user_pins_path(user)
        x = dict(w)

        await w.refresh(bot)  # refresh first to get cache

        try:
            # Open pins path.
            with p.open("r") as fp:
                j = json.loads(fp.read())  # returns dictionary
                fp.close()

                with p.open("w") as fw:

                    # Add to main bank

                    try:
                        j["pins"][identifier] = x
                    except KeyError:
                        j["user"] = str(user)
                        j["display_name"] = str(display_name)
                        j["pins"] = {identifier: x}

                    # Keep track of recents.

                    try:
                        # initialize new recents pinlist
                        userPinList = recentPins(
                            storage=j["recent_pins"].copy(),
                            capacity=__PINS_RECENTS_CAPACITY__,
                        )
                        userPinList.add(identifier)

                        j["recent_pins"] = userPinList.storage
                    except KeyError:
                        # empty
                        j["recent_pins"] = [identifier]

                    # Write to flie.
                    fw.write(json.dumps(j, sort_keys=True, indent=4))
                    fw.close()

                    return {
                        "status": "success",
                        "msg": f"Added Pin: {x}",
                        "pin": str(w),
                    }

        except (FileNotFoundError, json.decoder.JSONDecodeError):

            # Add to main bank and keep track of recents.
            j = {
                "user": str(user),
                "display_name": str(display_name),
                "pins": {identifier: x},
                "recent_pins": [identifier],
            }
            try:
                with p.open("w") as fw:
                    z = json.dumps(j, sort_keys=True, indent=4)
                    fw.write(z)
                    fw.close()

                    return {
                        "status": "success",
                        "msg": f"Added Pin: {x}",
                        "pin": str(w),
                    }
            except Exception as E:
                return {
                    "status": "failure",
                    "msg": list_printer([str(z) for z in E.args]),
                }

    @staticmethod
    async def remove_pin(user, payload):
        identifier = message_identifier(**payload)
        p = UserPins.user_pins_path(user)

        try:
            with p.open("r") as fr:
                j = json.loads(fr.read())
                fr.close()
            try:
                j["pins"].pop(identifier)

                logger.info("recent pins: " + list_printer(j["recent_pins"]))
                if identifier in j["recent_pins"]:
                    print("detected here")

                temp = j["recent_pins"] if j.get("recent_pins") else []
                userPinList = recentPins(
                    capacity=__PINS_RECENTS_CAPACITY__, storage=temp
                )

                userPinList.remove(identifier)
                j["recent_pins"] = userPinList.storage

                with p.open("w") as fw:
                    fw.write(json.dumps(j, sort_keys=True, indent=4))
                    logger.debug(f"Closing file {p}")
                    fw.close()
                return {"status": "success", "msg": f"Pin {identifier} removed."}

            except (KeyError, ValueError):
                return {
                    "status": "failure",
                    "msg": f'Pin "{identifier}" not found.',
                }
        except FileNotFoundError:
            return {
                "status": "failure",
                "msg": f"No pins file found for user {user} at {str(p)}",
            }
        except json.JSONDecodeError:
            return {"status": "failure", "msg": f"JSON file {str(p)} is empty."}

    @staticmethod
    async def get_pins(user, bot, number=__PINS_RECENTS_CAPACITY__):
        """gets a list of pins (the most recent 3)

        Args:
            user (str): user id in string format
            bot (discord.client): bot client
            number (int, optional): Number of recent pins to return (max). Defaults to 3.

        Returns:
            _type_: returns a dictionary with 'status' and 'msg'. Gives the client back a list newPins.
            Usage:
            for z in return['msg']
                # this is what we have...
                z.cache = {
                        "author": x["msg"].author.name,
                        "content": x["msg"].content,
                        "attachments_url": x["attachments_url"],
                        "date": fmt_date(x["msg"].created_at),
                    }
            or: for z in return['msg']: print(z)


        """
        # Need to create Pin objects from each JSON dictionary.
        # Instance of Pin Object does not require 'cache' key-val pair in the json dump.
        pins_path = UserPins.user_pins_path(user)

        try:
            with pins_path.open("r") as fp:
                x = json.loads(fp.read())
                pinlist = [
                    UserPins.newPin(
                        **dict(
                            (a, x["pins"][z][a])
                            for a in {"channel_id", "message_id", "cache"}
                        )
                    )
                    for z in recentPins(
                        storage=x["recent_pins"], capacity=__PINS_RECENTS_CAPACITY__
                    ).storage[0:number]
                ]
                for z in pinlist:
                    await z.refresh(bot)

                return {
                    "status": "success",
                    "msg": pinlist,
                }

        except KeyError:
            return {"status": "failure", "msg": []}
        except FileNotFoundError:
            return {"status": "failure", "msg": []}
        except json.decoder.JSONDecodeError:  # empty
            return {"status": "success", "msg": []}


class recentPins:
    def __init__(self, capacity=50, storage=[]):
        self.storage = storage
        self.capacity = capacity

    def add(self, identifier: str):
        logger.debug(f"Attemping to add {identifier} to list: {self.storage}")
        if identifier not in self.storage:
            self.storage.insert(0, identifier)
            if len(self.storage) > self.capacity:
                self.storage = self.storage[0 : self.capacity]

    def remove(self, identifier: str):
        try:
            self.storage.remove(identifier)
        except ValueError:
            raise ValueError(f"Recents Pinlist does not contain {identifier}")

    def __iter__(self):
        for x in self.storage:
            yield x

    def __str__(self):
        return str(self.storage)


if __name__ == "__main__":
    x = list(range(10))
    y = [str(z) for z in x]  # strings

    p = recentPins()
    for z in y:
        print(f"Adding {z}...")
        p.add(z)
        print(p, end="\n")
