import json

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.user.TrackedPanels import LatexImage, ParrotMessage, ShowPinsPanel
from discordbot_sloth.user.PseudoPins import message_identifier
from discordbot_sloth.user.newPin import StarredMessage

__STATE_FOLDER_NAME__ = "pins"


class State:
    @staticmethod
    def state_path(user):
        return __DATA_PATH__ / __STATE_FOLDER_NAME__ / (user + r"_pins.json")

    def __init_empty_config__(self):
        with State.state_path(self.user).open("w") as fw:
            print(f"Empty: {self.user}")
            x = dict()
            x["user"] = str(self.user)
            x["display_name"] = str(self.display_name)
            x["state"] = dict()
            x["pins"] = dict()
            fw.write(json.dumps(x, sort_keys=True, indent=4))
            fw.close

    # Reads from the json file.
    def __setup__(self):
        try:
            with State.state_path(self.user).open("r") as fp:

                try:
                    temp = json.loads(fp.read())
                except json.JSONDecodeError:  # empty file
                    self.__init_empty_config__()
                    self.__setup__()  # reload
                else:

                    try:
                        A = temp["state"]
                        # Create State Objects Here
                        self.state = dict()
                        for k, v in A.items():
                            if v.get("type"):
                                if v["type"] == "parrot_message":
                                    self.state[k] = ParrotMessage(**v["memory"])
                                elif v["type"] == "latex_image":
                                    self.state[k] = LatexImage(**v["memory"])
                                elif v["type"] == "pins_panel":
                                    self.state[k] = ShowPinsPanel(**v["memory"])

                    except KeyError:  # No 'state' field.
                        self.state = {}

                    try:
                        self.pins = temp["pins"]
                        A = temp["pins"]

                        # Create Pin Objects Here
                        self.pins = {(k, StarredMessage(**v)) for k, v in A.items()}
                    except KeyError:  # No 'pins' field
                        self.pins = {}

                finally:
                    fp.close()

        except FileNotFoundError:  # no file
            self.__init_empty_config__()
            self.__setup__()  # reload

    def __init__(self, user, bot):
        logger.debug(f"Init user: {user}")
        self.user = user
        self.display_name = bot.get_user(int(user)).name

        self.__setup__()

    # Belongs in state class
    async def get(self, identifier="", type=""):

        x = self.state.get(identifier)  # should be a dictionary
        # can replace this by another class but we will skip this for now.
        # a class that allows us to use x = AbstractLink(**self.state.get(identifier))

        # TODO: implement sorting by type.
        # i.e get all by type

        if x is None:

            return x

        if x["type"] == "parrot_message":
            return ParrotMessage(**x["memory"])
        elif x["type"] == "latex_image":
            return LatexImage(**x["memory"])
        elif x["type"] == "pins_panel":
            return ShowPinsPanel(**x["memory"])

    # No need a separate edit method

    def save(self):

        # Clean up Dead Panels
        temp = self.state.copy()
        z = lambda a: bool(a.get("type")) and a.get("type") != "dead"

        temp = {k: v for k, v in temp.items() if z(v)}
        self.state = temp

        try:

            A = {
                "display_name": self.display_name,
                "state": {(k, dict(v)) for k, v in self.state.items()},
                "pins": {(k, dict(v)) for k, v in self.pins.items()},
            }

            with State.state_path(self.user).open("w") as fw:
                fw.write(json.dumps(A, sort_keys=True, indent=4))
                fw.flush()
                fw.close()
        except Exception as E:
            return {"status": "failure", "msg": list_printer([str(z) for z in E.args])}
        finally:
            return {
                "status": "success",
                "msg": f"Saved to {State.state_path(self.user)}",
            }

    def __str__(self):
        return str(self.state)

    def add_pin(self, identifier, bot):
        pass
        logger.debug(f"Adding Pin: {identifier}")
