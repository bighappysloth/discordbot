#argparse helpers
#json/dictionary -> fast subparsers and commands.
import argparse
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


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest = 'command',required = True)

"""
    Make a Function to handle adding subparsers.
"""



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

# List of Argparse methods
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

result = helper_add_subparsers(subparsers, C)