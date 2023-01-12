import logging

from pathlib import Path
import json


from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.user.State import __STATE_FOLDER_NAME__
from discordbot_sloth.user.State import State

logger = logging.getLogger(__name__)

def load_states(bot):
    STATE_FOLDER_PATH = __DATA_PATH__ / __STATE_FOLDER_NAME__

    x = [Path(z) for z in STATE_FOLDER_PATH.glob('*.json')]
    y = [str(z.stem)[:-5] for z in x]
    A = dict((user, State(user, bot)) for user in y )
    return A
        
        
def save_states(bot):
    
    A = bot.states
    
    for k, v in A.items():
        v.save()
        

# def new_state(user, bot):
#     z = {
#         'display_name': bot.get_user(int(user)).name,
#         'pins':         {},
#         'state':        {},
#     }
#     return z
        



class foo:
    pass


if __name__ == '__main__':
    x = foo()
    load_states(x)