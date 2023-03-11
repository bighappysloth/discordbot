import json
import logging
import os

from discordbot_sloth.user.default_settings import (
    __DEFAULT_CONFIG_PATH__,
    __COMMAND_DEFAULT_SETTINGS__,
    __DEFAULT_USER__,
    __CONFIG_FOLDER_PATH__,
    DEFAULT_CONFIG,
)
from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.dictionary_searching import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.module_args.matplotlib_args import *
from discordbot_sloth.user.allowed_settings import ALLOWED_CONFIG


logger = logging.getLogger(__name__)

"""
Configuration Class
"""


class Configuration:
    @staticmethod
    def getDefaultConfig():
        return viewFullUserConfig(__DEFAULT_USER__)["payload"]

    @staticmethod
    def getPrettyDefaultConfig():  # unused
        return viewFullUserConfig(__DEFAULT_USER__)["msg"]

    def __init__(self, user=__DEFAULT_USER__):

        self.user = user
        temp = viewFullUserConfig(self.user)
        if temp["status"] != "success":
            # logger.debug(f'Configuration __init__ error: {self.user}, reason: {temp}')
            """
            If there is an empty file or no file at all, then we load the default config, while keeping track of the user's ID.

            This is to support future editing.
            """
            temp = viewFullUserConfig(__DEFAULT_USER__)

            if temp["status"] != "success":
                raise ValueError("Configuration loader has failed.")

        self.settings = temp["payload"]

        # logger.debug(f'Configuration Init: {user} --> {z}')

    def getEntry(self, selected_option):
        """Gets an config entry

        Args:
            selected_option (str): dotted hierarchical notation

        Returns:
            Any: the value field, if some type of error occurs, attempts ot fetch default settings.
        """

        z = getEntryRecursive_dictionary(selected_option, self.settings)

        if z["status"] != "success":

            if self.user != __DEFAULT_USER__:
                # One last try: Searches in Default Config
                
                temp = viewFullUserConfig(__DEFAULT_USER__)["payload"]
                default_result = getEntryRecursive_dictionary(selected_option, temp)
                return default_result
        return z

    def editEntry(self, selected_option, new_value, write=True):

        z = getEntryRecursive_dictionary(
            selected_option, Configuration.getDefaultConfig()
        )
        if z["status"] != "success":
            return {
                "status": "failure",
                "msg": f"Option `{selected_option}` not found.",
            }
        else:
            # There exists such an option to edit. Now we have to check for validity.

            entry_validation_test = getEntryRecursive_dictionary(
                selected_option, ALLOWED_CONFIG
            )
            try:
                if selected_option.lower() == 'true':
                    selected_option = True
                elif selected_option.lower() == 'false':
                    selected_option = False
                    
                if entry_validation_test["status"] == "success":
                    entry_validation_test["msg"](new_value, selected_option)

            except (ValueError, TypeError) as E:
                logger.warning(f"E: {E.args}, {type(E.args)}")
                return {
                    "status": "failure",
                    "msg": "```" + list_printer([str(z) for z in E.args]) + "```",
                }
            else:
                """
                Enters this block if and only if we pass the test or if there is no test at all.
                """
                temp_query = selected_option.split(".")
                temp_dictionary = self.settings
                while len(temp_query) != 1:
                    temp_dictionary = temp_dictionary[temp_query[0]]
                    temp_query = temp_query[1:]
                old_value = self.settings.get(selected_option)

                # updates self.settings
                temp_dictionary[temp_query[0]] = new_value
                path_to_settings = user_settings_path(self.user)

                # logger.debug(f'path_to_settings: {path_to_settings}')
                if write:  # Writes to disk if flag is enabled.
                    with path_to_settings.open("w") as fp:
                        fp.write(json.dumps(self.settings, sort_keys=True, indent=4))
                        fp.flush()
                        fp.close()
                return {
                    "status": "success",
                    "msg": f'{selected_option}: {old_value if old_value!=None else (f"{Configuration(__DEFAULT_USER__).getEntry(selected_option)} (default)")} -> {new_value}.',
                }

    def reload(self):
        self.settings = viewFullUserConfig(self.user)["payload"]

    @staticmethod
    def restoreUserConfig(user):

        try:

            temp = Configuration(user)
            usage = int(temp.getEntry("usage"))
            logger.debug(f"old usage: {usage}")

            settings_path = user_settings_path(user)
            if settings_path:
                os.remove(settings_path)
            temp2 = Configuration(user)
            temp2.editEntry("usage", usage)
            temp2.editEntry("last_used", current_time())
            return {"status": "success", "msg": "Restore successful"}
        except Exception as E:
            return {
                "status": "failure",
                "msg": "```\n" + list_printer([str(z) for z in E.args]) + "\n```",
            }

    @staticmethod
    def incrementUserConfig(user, cmd):
        if user != __DEFAULT_USER__:
            x = Configuration(user)
            new_usage = x.getEntry("usage")["msg"] + 1
            x.editEntry("usage", new_usage, write=True)
            x.editEntry("last_used", current_time(), write=True)
            x.editEntry("last_command", cmd, write = True)
            return
        raise ValueError("Default User cannot be incremented.")


def user_settings_path(user):
    """
    Helper Method to generate user settings path.
    TODO: implement as static method within Configurations
    """
    return __CONFIG_FOLDER_PATH__ / (user + r"_settings.json")


def getUserConfig(user, user_option="usage"):
    """
    TODO: implement this as a static method within Configurations
    """
    settings_path = user_settings_path(user)
    try:
        with settings_path.open("r") as f:
            j = json.loads(f.read())
            return j[user_option]
    except (FileNotFoundError, KeyError):
        try:
            # Try resorting to DEFAULT_CONFIG, if the user has not configured this option yet.
            return getUserConfig(__DEFAULT_USER__)[user_option]
        except KeyError:
            raise KeyError(f'Option "{user_option}" does not exist.')


def viewFullUserConfig(user):
    """
    TODO: implement this as a static method within Configurations
    viewFullUserConfig(user) returns a dictionary with status: 'success' or 'failure'. Gives the dictionary in two formats, string (in 'msg') and 'payload' only on success.
    """
    settings_path = user_settings_path(user)
    try:
        with settings_path.open("r") as fp:

            j = json.dumps(json.loads(fp.read()), sort_keys=True, indent=4)

            # print(f'JSON DUMP View Full user Config:\n{j}')

            return {"status": "success", "msg": j, "payload": json.loads(j)}
    except FileNotFoundError:
        return {
            "status": "failure",
            "msg": f"User {user} has no config file. Default parameters are used instead. !config [option] [new_value] to edit, and {__COMMAND_DEFAULT_SETTINGS__} for help.",
        }
    except json.decoder.JSONDecodeError:
        j = viewFullUserConfig(__DEFAULT_USER__)["msg"]

        return {"status": "success", "msg": j, "payload": json.loads(j)}


"""
This function is outdated and should be removed as soon as possible.
"""


def editUserConfig(user: str, user_option: str, new_value):
    settings_path = user_settings_path(user)

    try:
        with settings_path.open("r") as fp:
            j = json.loads(fp.read())  # returns a dictionary

            temp = DEFAULT_CONFIG[user_option]  # Just to trigger the KeyError

            if ALLOWED_CONFIG.get(user_option):
                ALLOWED_CONFIG[user_option](new_value, user_option)

            fp.close()
            with settings_path.open("w") as fw:
                old_value = j.get(user_option)
                j[
                    user_option
                ] = new_value  # After checking for Valid Arguments (if there exists a check)
                fw.write(json.dumps(j, sort_keys=True, indent=4))
                fw.close()

                return {
                    "status": "success",
                    "msg": f'{user_option}: {old_value if old_value!=None else (f"{DEFAULT_CONFIG.get(user_option)} (default)")} -> {new_value}.',
                }
    except FileNotFoundError:
        try:
            if new_value == DEFAULT_CONFIG[user_option]:
                return {
                    "status": "success",
                    "msg": f"{user_option}: {new_value} -> {DEFAULT_CONFIG[user_option]} (default).",
                }
            else:
                with settings_path.open("w") as fp:
                    z = json.dumps(
                        {user_option: new_value}, sort_keys=True, indent=4
                    )  # Need to check for TypeError as well.
                    fp.write(z)
                    fp.close()
        except KeyError:
            return {"status": "failure", "msg": f'Unknown option "{user_option}".'}

    except KeyError:
        return {"status": "failure", "msg": f'Unknown option "{user_option}".'}

    except (ValueError, TypeError) as E:  # fails the restriction imposed.
        return {
            "status": "failure",
            "msg": E.args,
        }
    except Exception as E:
        return {
            "status": "failure",
            "msg": E.args,
        }
