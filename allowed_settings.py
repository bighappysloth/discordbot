import datetime 

# Type Checks

def helper_range_check(x,min,max,required_type,user_option):
    if not isinstance(x, required_type): raise TypeError(f'Value {user_option} must be of type {required_type}.')
    if not (min <= x and x <= max): raise ValueError(f'Value {user_option} must lie between {min} and {max}.')


def helper_set_check(x,required_set:set,user_option):
    if x==None: raise TypeError(f'Value {user_option} cannot be None.')
    if not x in required_set: raise ValueError(f'Value {user_option} must be in {required_set}.')


def helper_type_check(x,required_type,user_option):
    if not isinstance(x, required_type): raise TypeError(f'Value {user_option} must be of type {required_type}.')
    
    
"""
Maps a field to a lambda expression that raises exceptions. Use with ALLOWED_CONFIG[field](new_value, field) perhaps after checking with ALLOWED_CONFIG.get(field)
"""
ALLOWED_CONFIG = {\
    'latex_mode': 			lambda x, y: helper_set_check(x,{'inline','display'},y),

    'framing': 			    lambda x, y: helper_set_check(x,{'regular', 'tight','wide'},y),

    'latex_preamble': 		lambda x, y: helper_type_check(x, str,y),

    'usage': 			    lambda x, y: helper_type_check(x, int,y),

    'last_used': 			lambda x, y: (helper_type_check(x, str,y) or x==None),

    'background': 			lambda x, y: helper_type_check(x, str,y),

    'png_dpi': 			    lambda x, y: helper_range_check(x,200,6000,int,y),

    'plot_samples': 		lambda x, y: helper_range_check(x,100,1200,int,y),

    'plot_grid': 			lambda x, y: helper_type_check(x, bool,y),

    'plot_xlimits': 		lambda x, y: helper_type_check(x , list,y) and helper_type_check(x[0], int,y) and helper_type_check(x[1], int,y) and x[0]<x[1],

}