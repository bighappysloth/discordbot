import json

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.user.StarredMessage import StarredMessage
from discordbot_sloth.user.TrackedPanels import (LatexImage, ParrotMessage,
                                                 ShowPinsPanel)

__STATE_FOLDER_NAME__ = "pins"
__STATE_FOLDER_PATH__ = __DATA_PATH__ / __STATE_FOLDER_NAME__

class State:
    @staticmethod
    def state_path(user):
        return __DATA_PATH__ / __STATE_FOLDER_NAME__ / (user + r"_pins.json")

    def __init_empty_config__(self):
        with State.state_path(self.user).open("w") as fw:
            # print(f"Empty: {self.user}")
            x = dict()
            x["user"] = str(self.user)
            x["display_name"] = str(self.display_name)
            x["state"] = dict()
            x["pins"] = dict()
            fw.write(json.dumps(x, sort_keys=True, indent=4))
            fw.close()

    # Reads from the json file.
    def __setup__(self):
        try:
            with State.state_path(self.user).open("r") as fp:

                try:
                    temp = json.loads(fp.read())

                    # Loading State
                    try:
                        A = dict(temp["state"])
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
                        self.state = dict()

                    # Loading Pins
                    try:
                        self.pins = dict(temp["pins"])
                        A = dict(temp["pins"])
                        # logger.debug(f'Loading State for user {self.display_name}: {dict_printer(A)}')

                        # Create Pin Objects Here
                        
                        self.pins = dict()
                        for (k, v) in A.items():
                            self.pins[k] = StarredMessage(**v)

                        # logger.debug(f'{self.user} pins: {len(self.pins)}')

                    except KeyError:  # No 'pins' field
                        self.pins = dict()

                except json.JSONDecodeError:  # empty file
                    self.__init_empty_config__()
                    self.__setup__()  # reload

                finally:
                    fp.close()

        except FileNotFoundError:  # no file
            logger.warning(f'No File Found for user: {self.user}')
            self.__init_empty_config__()
            self.__setup__()  # reload

        if isinstance(self.state, set):
            self.state = dict()
        if isinstance(self.pins, set):
            self.pins = dict()

    def __init__(self, user, bot):
        
        self.user = user
        self.display_name = bot.get_user(int(user)).name
        logger.debug(f"Init user: {user}/{self.display_name}")
        self.__setup__()

    # Belongs in state class
    async def fetch_tracker(self, identifier="", type=""):
        """Using a message identifier we get a TrackedMessage

        Args:
            identifier (str, optional): Message Identifier. If left blank then we assume the client wants to retrieve all TrackedMessages with a certain type. Defaults to "".
            type (str, optional): type of tracked message. Both fields cannot be blank. Defaults to "".

        Returns:
            AbstractPanel: a subclass of AbstractPanel.

        """

        # TODO: implement sorting by type.
        # i.e get all by type

        if identifier:
            x = self.state.get(identifier)
            if x is None:
                return x

            if x["type"] == "parrot_message":
                return ParrotMessage(**x["memory"])
            elif x["type"] == "latex_image":
                return LatexImage(**x["memory"])
            elif x["type"] == "pins_panel":
                return ShowPinsPanel(**x["memory"])
        else:
            # User does not provide an identifier
            if type:
                if type == "parrot_message":
                    y = lambda a: isinstance(a, ParrotMessage)
                elif type == "latex_image":
                    y = lambda a: isinstance(a, LatexImage)
                elif type == "pins_panel":
                    y = lambda a: isinstance(a, ShowPinsPanel)
                else:
                    # None others are filtered through.
                    return []
                z = list(self.state.values())
                z = list(filter(y, z))
                return z

    def __iter__(self):
        out = {
            "display_name": self.display_name,
            "state": dict((x, dict(y)) for x, y in self.state.items()),
            "pins": dict((x, dict(y)) for x, y in self.pins.items()),
        }
        for k, v in out.items():
            yield (k, v)

    # No need a separate edit method

    def save(self):

        # Clean up Dead Panels

        try:

            # A = {
            #     "display_name": self.display_name,
            #     "state": {(k, dict(v)) for k, v in self.state.items()},
            #     "pins": {(k, dict(v)) for k, v in self.pins.items()},
            # }

            A = dict(self)
            print(f"Dict for user {self.user}: {A}")
            p = Path(State.state_path(self.user))
            logger.debug(f"Saving to {str(p)}")
            with p.open("w") as fw:
                fw.seek(0)
                fw.write(json.dumps(A, sort_keys=True, indent=4))
                fw.flush()
                fw.close()
            # logger.debug(f"Finished Saving to {p}")
        except Exception as E:
            logger.warning(f"Something went wrong... {E.args}")
            return {"status": "failure", "msg": list_printer([str(z) for z in E.args])}
        finally:
            return {
                "status": "success",
                "msg": f"Saved to {State.state_path(self.user)}",
            }

    def __str__(self):
        z = self.state
        s = self.pins
        x = f"States: {z}\nPins: {s}"
        return x

    def add_pin(self, identifier, bot):
        pass
        logger.debug(f"Adding Pin: {identifier}")
        
    async def write_to_txt(self):
        txt_dir = Path(__STATE_FOLDER_PATH__ / 'txt_out')
        txt_path = txt_dir / (f'{self.user}.txt')
        check_dir(txt_dir) # Checks if the directory exists.
        
        contents = json.dumps(dict(self), indent = 4, sort_keys = True)
        
        
        try:
            with txt_path.open('w') as f:
                f.seek(0)
                f.write(contents)
                f.close()
            logger.debug(f'Writing to {str(txt_path)}')
            return {'status': 'success', 'msg': '', 'Path': txt_path}
        
        except Exception as e:
        
            return {'status': 'failure', 'msg': str(e), 'Path': ''}

        