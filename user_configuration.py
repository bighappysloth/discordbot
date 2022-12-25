import argparse
import datetime
from pathlib import Path
import json
import os

from allowed_settings import ALLOWED_CONFIG


__DEFAULT_USER__ = 'ccE' #Change this afterwards


__DEFAULT_CONFIG_PATH__ = Path('.') / r'default_settings.json'

DEFAULT_CONFIG = {\
'latex_mode': 'inline',
'framing': 'regular',
'latex_preamble': '',
'usage': 0,
'last_used': None,
'background': 'white',
'png_dpi': 2400,
'plot_samples': 100,
'plot_grid': True,
'plot_xlimits': [0,10],
'matplotlib_settings': {\
                            'plot': {
                                'color': 'tab:orange',
                                'linewidth': 2.5,
                            },
                            'legend':{
                                'loc': 'upper right',
                            
                            },
                        },
'xprint_settings': {\
                    'verb': True,
                    'env': 'regular',
                    'latex_mode': 'inline',
                    
                    }


}

"""
Initialize Default Config from __DEFAULT_CONFIG_PATH__
"""

try:
    with __DEFAULT_CONFIG_PATH__.open('r') as fp:
        __DEFAULT__CONFIG__ = json.loads(fp.read())
except FileNotFoundError: pass
    





_COMMAND_DEFAULT_SETTINGS = 'default'
parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest = 'command',required = True)

"""
    Make a Function to handle adding subparsers.
"""

def safeMerge(D:dict,K:str,L:list):
    """
    If D[K] does not exist, then do nothing,
    If D[K] is iterable, then extend L with all elements within D[K]
    If D[K] is not iterable, then append D[K] to L.
    """
    try:
        iterator = iter(D.get(K))
    except TypeError:
        # Not iterable
        if D.get(K): L.append(D.get(K)) # Check if None
    else:
        if isinstance(D.get(K),str): 
            L.append(D.get(K))
        else: 
            L.extend(D.get(K))
    return L


def printAll(*args, **kwargs):
    print(f'positional: {args}')
    print(f'keyword: {kwargs}')

def helper_add_subparsers(subparser:argparse._SubParsersAction, payload:dict):
    result = {}
    
    for subcommand in payload:

        temp = subparser.add_parser(subcommand)
        
        for arg in payload[subcommand]:
            positional = [arg] # List with one element. 
            
            safeMerge(payload[subcommand][arg], 'aliases', positional)

            # print(f'subcommand: {subcommand}, {positional}, {payload[subcommand][arg]["arg_options"]}')
            
            temp.add_argument(*positional, **payload[subcommand][arg]['arg_options'])
        result[subcommand] = temp
    return result


C = {\
    'view': {
        # 'user_option': {
        #     'arg_options': {
        #         'type': str,
        #         'help': 'The option to edit.',
        #         'default': r'__ALL__',
        #         'required': False
        #     } 
        # },
        '-verbose': {
            'arg_options': {
                'action': 'store_true',
                'required': False
            },
            'aliases': '-v'
        }   
    },
    'edit': {
        'user_option': {
            'arg_options': {
                'type': str,
                'help': 'The option to edit.'
            } 
        },
        'new_value': {
            'arg_options': {
                'type': str,
                'help': 'The value to change it to.'
            }
        }
    },
    'restore': {
    
    },
}

"""
Generate Config
"""



def user_settings_path(user):
    """
    Helper Method to generate user settings path.
    """
    p = Path('.')
    return p/(user + r'_settings.json')


def getUserConfig(user, user_option='usage'):
    settings_path = user_settings_path(user)
    try:
        with settings_path.open('r') as f: 
            j = json.loads(f.read())
            return j[user_option]
    except (FileNotFoundError, KeyError):
        try: 
            # Try resorting to DEFAULT_CONFIG, if the user has not configured this option yet.
            return DEFAULT_CONFIG[user_option]
        except KeyError:
            raise KeyError(f'Option "{user_option}" does not exist.')


def viewUserConfig(user, user_option='usage'):
    settings_path = user_settings_path(user)
    try:
        value = getUserConfig(user,user_option)
        return f'{user_option}: {value}'
    except KeyError as E:
        return E.args


def viewFullUserConfig(user):
    settings_path = user_settings_path(user)
    try:
        with settings_path.open('r') as fp:
            j = json.dumps(json.loads(fp.read()),sort_keys=True, indent=4)
            return j
    except FileNotFoundError:
        return f'User {user} has no config file. Default parameters are used instead. See {_COMMAND_DEFAULT_SETTINGS}.'
            

def editUserConfig(user:str, user_option:str, new_value):
    settings_path = user_settings_path(user)
    try:
        with settings_path.open('r') as fp:
            j = json.loads(fp.read()) # returns a dictionary
            
            temp = DEFAULT_CONFIG[user_option] # Just to trigger the KeyError

            if ALLOWED_CONFIG.get(user_option): ALLOWED_CONFIG[user_option](new_value,user_option)
            fp.flush()
            fp.close()
        with settings_path.open('w') as fw:

            j[user_option] = new_value # After checking for Valid Arguments (if there exists a check)
            fw.write(json.dumps(j))

            
    except FileNotFoundError:
        try:
            if new_value == DEFAULT_CONFIG[user_option]:
                return {
                    'status': 'success',
                    'msg': f'{user_option}: {new_value} -> {DEFAULT_CONFIG[user_option]} (default).'
                }
            else:
                with settings_path.open('w') as fp:
                    z = json.dumps({user_option: new_value}) #Need to check for TypeError as well.
                    fp.write(z)
        except KeyError:
            return {
            'status': 'failure',
            'msg': f'Unknown option "{user_option}".'
            }
    
    except KeyError:
        return {
            'status': 'failure',
            'msg': f'Unknown option "{user_option}".'
        }
        
    except (ValueError, TypeError) as E:
        return {
            'status': 'failure',
            'msg': E.args,
        }
    except Exception as E:
        return {
            'status': 'failure',
            'msg': E.args,
        }
        
        
def restoreUserConfig(user):
    Z = {'usage','last_used'} # do not wipe these entries.
    for k in DEFAULT_CONFIG:
        if not k in Z:
            editUserConfig(user, k, DEFAULT_CONFIG[k]) # wipe all config.
    # Call our incrementing function


# with settings_path.open('w') as f:
#     f.write(json.dumps(DEFAULT_CONFIG))
#     print(f'Writing to {settings_path}...')

# with settings_path.open('r') as f:
#     j = json.loads(f.read())
#     print(f'Printing JSON Settings: {j},\ntype: {type(j)}')

result = helper_add_subparsers(subparsers, C)
# print(result)


#print(getUserConfig('ccE', 'latex_mode'))
# print(viewUserConfig(__DEFAULT_USER__, 'xprint_settings'))


# print(viewFullUserConfig(__DEFAULT_USER__))
if __name__ == '__main__':
    args = parser.parse_args()
    current_user = __DEFAULT_USER__

    if args.command == 'view':
        print(f'Command Selected: {args.command}')
        print(viewFullUserConfig(user=current_user))

    elif args.command =='edit':
        print(f'Command Selected: {args.command} w/ {args}')
        print(editUserConfig(user=current_user, user_option = args.user_option, new_value = args.new_value))

    elif args.command == 'restore':
        print(f'Command Selected: {args.command}')
        print(restoreUserConfig(user=current_user))

# TODO: Load all User Configurations at Startup, then
# on editing any of the files, save it to disk. And reload.