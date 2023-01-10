"""
Defines the settings and their permissible values. 
"""
import discordbot_sloth.module_args.matplotlib_args as matplotlib_args
import discordbot_sloth.module_args.latex_args as latex_args


def helper_range_check(x,
                       min,
                       max,
                       required_type,
                       user_option):

    if not isinstance(x, required_type):
        try:
            z=int(x)
        except ValueError:
            raise TypeError(
                f'Value {user_option} must be of type {required_type}.')
        else:
            return z

    if not (min <= x and x <= max):
        raise ValueError(
            f'Value {user_option} must lie between {min} and {max}.')


def helper_set_check(x,
                     required_set: set,
                     user_option,
                     usage_help=None
                     ):

    if x == None:
        raise TypeError(f'Value {user_option} cannot be None.')

    if not x in required_set:
        if not usage_help:
            raise ValueError(f'Value {user_option} must be in {required_set}.')
        else:
            raise ValueError(
                f'Value {user_option} must satisfy: '+ '\n' +f'{usage_help}')


def helper_type_check(x, required_type, user_option):
    if not isinstance(x, required_type):
        raise TypeError(
            f'Value {user_option} must be of type {required_type}.')


"""
Maps a field to a lambda expression that raises exceptions. Use with ALLOWED_CONFIG[field](new_value, field) perhaps after checking with ALLOWED_CONFIG.get(field)
"""
ALLOWED_CONFIG = {
    'latex_mode': lambda x, y: helper_set_check(x, {'inline', 'display','raw'}, y),

    'framing': lambda x, y: helper_set_check(x, {'regular', 'tight', 'wide'}, y),

    'latex_preamble': lambda x, y: helper_type_check(x, str, y),

    'usage': lambda x, y: helper_type_check(x, int, y),

    'last_used': lambda x, y: (helper_type_check(x, str, y) or x == None),

    'background': lambda x, y: helper_type_check(x, str, y),

    'png_dpi': lambda x, y: helper_range_check(x, 200, 6000, int, y),

    'plot_samples': lambda x, y: helper_range_check(x, 100, 1200, int, y),

    'plot_grid': lambda x, y: helper_type_check(x, bool, y),

    'plot_xlimits': lambda x, y: helper_type_check(x, list, y) and helper_type_check(x[0], int, y) and helper_type_check(x[1], int, y) and x[0] < x[1],
    'matplotlib_settings':  {
        'legend': {
            'loc': lambda x, y: helper_set_check(x,
                                                 matplotlib_args.allowed_legend_locations,
                                                 y,
                                                 matplotlib_args.legend_location_usage_string),
        },
        'plot': {
            'color': lambda x, y: helper_set_check(x,
                                                   matplotlib_args.allowed_colours,
                                                   y,
                                                   matplotlib_args.colour_usage_string),
            'linewidth': lambda x, y: helper_range_check(x,
                                                         0.5,
                                                         5,
                                                         float,
                                                         y),

        }
    },
    'xprint_settings':  {
        'verb': lambda x, y: helper_type_check(x, bool, y),
        'env': lambda x, y: helper_set_check(x,
                                             latex_args.matrix_environments,
                                             y,
                                             latex_args.allowed_env_usage_string
                                             ),
        'latex_mode': lambda x, y: helper_set_check(
            x,
            latex_args.latex_modes,
            y,
            latex_args.allowed_latex_modes_usage_string
        ),
        'use_title': lambda x, y: helper_type_check(x, bool, y),

    },

}
