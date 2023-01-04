from pathlib import Path
import json
import logging

from allowed_settings import ALLOWED_CONFIG
from dictionary_searching import getEntryRecursive_dictionary # Recursive Methods for parsing hierarchical expressions.
import bot_helpers
import module_configs.matplotlib_args as matplotlib_args

__DEFAULT_USER__ = 'default' # name of the default user

__CONFIG_FOLDER_NAME__ = r'user_settings'

__CONFIG_FOLDER_PATH__ = Path('.')/ __CONFIG_FOLDER_NAME__

__DEFAULT_CONFIG_PATH__ = __CONFIG_FOLDER_PATH__/ r'default_settings.json'


__COMMAND_DEFAULT_SETTINGS__ = '!defaults'


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
    
"""
Configuration Class
"""
class Configuration:

    @staticmethod
    def getDefaultConfig():
        return viewFullUserConfig(__DEFAULT_USER__)['payload']
    
    @staticmethod
    def getPrettyDefaultConfig(): # unused
        return viewFullUserConfig(__DEFAULT_USER__)['msg']

    def __init__(self, user=__DEFAULT_USER__):

        self.user = user
        temp = viewFullUserConfig(self.user)
        if temp['status']!='success': 
            
            temp = viewFullUserConfig(__DEFAULT_USER__)
            
            if temp['status']!='success': raise ValueError('Configuration loader has failed.')

            self.user=__DEFAULT_USER__ # reset to default user
        
        self.settings=temp['payload']
        # print(f'see here{self.settings}')
        z = json.dumps(self.settings,sort_keys=True,indent=4)
        # print(f'Configuration Init: {user} --> {z}')
                

        
    
    def getEntry(self, selected_option):
        
        z = getEntryRecursive_dictionary(selected_option,self.settings)

        if z['status']!='success':
            
            if self.user!=__DEFAULT_USER__:
                # One last try: Searches in Default Config
                temp = viewFullUserConfig(__DEFAULT_USER__)['payload']
                default_result = getEntryRecursive_dictionary(selected_option,temp)
                return default_result
        return z


    def editEntry(self, selected_option, new_value, write=True):
        
        z = getEntryRecursive_dictionary(selected_option, 
        Configuration.getDefaultConfig())
        if z['status']!='success':
            return {
                'status': 'failure',
                'msg': f'Option `{selected_option}` not found.'
            }
        else:
            # There exists such an option to edit. Now we have to check for validity.

            entry_validation_test = getEntryRecursive_dictionary(selected_option, ALLOWED_CONFIG)
            try:
                if entry_validation_test['status']=='success':
                    entry_validation_test['msg'](new_value,selected_option)
            
            except (ValueError,TypeError) as E:
                print(f'E: {E.args}, {type(E.args)}')
                return {
                    'status': 'failure',
                    'msg': '```' + matplotlib_args.HelperString.list_printer([str(z) for z in E.args]) + '```'
                }
            else:
                """
                Enters this block if and only if we pass the test or if there is no test at all. 
                """
                temp_query = selected_option.split('.')
                temp_dictionary = self.settings
                while len(temp_query)!=1:
                    temp_dictionary = temp_dictionary[temp_query[0]]
                    temp_query = temp_query[1:]
                old_value = self.settings.get(selected_option)

                
                temp_dictionary[temp_query[0]]=new_value # updates self.settings
                path_to_settings = user_settings_path(self.user) 
                
                
                if write: # Writes to disk if flag is enabled.
                    with path_to_settings.open('w') as fp:
                        fp.write(json.dumps(self.settings, sort_keys=True, indent = 4))
                        fp.flush()
                        fp.close()
                return {
                    'status': 'success',
                    'msg': f'{selected_option}: {old_value if old_value!=None else (f"{Configuration(__DEFAULT_USER__).getEntry(selected_option)} (default)")} -> {new_value}.'
                }
            

    def reload(self):
        self.settings = viewFullUserConfig(self.user)['payload']


    @staticmethod
    def restoreUserConfig(user):
        Z = {'usage','last_used'} # do not wipe these entries.
        for k in DEFAULT_CONFIG:
            if not k in Z:
                editUserConfig(user, k, DEFAULT_CONFIG[k]) # wipe all config.
        # Call our incrementing function


    @staticmethod
    def incrementUserConfig(user):
        if user!=__DEFAULT_USER__:
            x = Configuration(user)
            new_usage = x.getEntry('usage')['msg'] + 1
            z1=x.editEntry('usage',new_usage,write=True)
            z2=x.editEntry('last_used',bot_helpers.current_time(),write = True)
            logging.debug(f'First, Second: {z1}, {z2}')
            logging.debug(f'new_usage: {new_usage}, type={type(new_usage)}')
            return
        raise ValueError('Default User cannot be incremented.')

    


def user_settings_path(user):
    """
    Helper Method to generate user settings path.
    TODO: implement as static method within Configurations
    """
    return __CONFIG_FOLDER_PATH__/(user + r'_settings.json')


def getUserConfig(user, user_option='usage'):
    """
    TODO: implement this as a static method within Configurations
    """
    settings_path = user_settings_path(user)
    try:
        with settings_path.open('r') as f: 
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
    """
    settings_path = user_settings_path(user)
    try:
        with settings_path.open('r') as fp:
            
            j = json.dumps(json.loads(fp.read()),sort_keys=True, indent=4)
            
            # print(f'JSON DUMP View Full user Config:\n{j}')
            
            return {
                'status': 'success',
                'msg': j,
                'payload': json.loads(j)
            }
    except FileNotFoundError:
        return {
            'status': 'failure',
            'msg': f'User {user} has no config file. Default parameters are used instead. !config [option] [new_value] to edit, and {__COMMAND_DEFAULT_SETTINGS__} for help.',
        }
    except json.decoder.JSONDecodeError:
        j = viewFullUserConfig(__DEFAULT_USER__)['msg']
        
        return{
            'status': 'failure',
            'msg':  j,
            'payload': json.loads(j)    
        }
            
"""
This function is outdated and should be removed as soon as possible.
"""
def editUserConfig(user:str, user_option:str, new_value):
    settings_path = user_settings_path(user)
    try:
        with settings_path.open('r') as fp:
            j = json.loads(fp.read()) # returns a dictionary
            
            temp = DEFAULT_CONFIG[user_option] # Just to trigger the KeyError

            if ALLOWED_CONFIG.get(user_option): ALLOWED_CONFIG[user_option](new_value,user_option)
            
            fp.close()
            with settings_path.open('w') as fw:
                old_value = j.get(user_option)
                j[user_option] = new_value # After checking for Valid Arguments (if there exists a check)
                fw.write(json.dumps(j))
                fw.close()

                return {
                    'status': 'success',

                    'msg': f'{user_option}: {old_value if old_value!=None else (f"{DEFAULT_CONFIG.get(user_option)} (default)")} -> {new_value}.'
                }
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
                    fp.close()
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
        
    except (ValueError, TypeError) as E: # fails the restriction imposed.
        return {
            'status': 'failure',
            'msg': E.args,
        }
    except Exception as E:
        return {
            'status': 'failure',
            'msg': E.args,
        }
        
        


# with settings_path.open('w') as f:
#     f.write(json.dumps(DEFAULT_CONFIG))
#     print(f'Writing to {settings_path}...')

# with settings_path.open('r') as f:
#     j = json.loads(f.read())
#     print(f'Printing JSON Settings: {j},\ntype: {type(j)}')


# print(result)


#print(getUserConfig('ccE', 'latex_mode'))
# print(viewUserConfig(__DEFAULT_USER__, 'xprint_settings'))


# print(viewFullUserConfig(__DEFAULT_USER__))

# Additional Testing for Configuration

# if __name__ == '__main__':
#     args = parser.parse_args()
#     current_user = __DEFAULT_USER__

#     if args.command == 'view':
#         print(f'Command Selected: {args.command}')
#         print(viewFullUserConfig(user=current_user))

#     elif args.command =='edit':
#         print(f'Command Selected: {args.command} w/ {args}')
#         print(editUserConfig(user=current_user, user_option = args.user_option, new_value = args.new_value))

#     elif args.command == 'restore':
#         print(f'Command Selected: {args.command}')
#         print(restoreUserConfig(user=current_user))

# TODO: Load all User Configurations at Startup, then
# on editing any of the files, save it to disk. And reload.