from discordbot_sloth.helpers.RegexReplacer import *

# Allowed Colors:

tab_colours = \
    [
        'tab:blue',
        'tab:orange',
        'tab:green',
        'tab:red',
        'tab:purple',
        'tab:brown',
        'tab:pink',
        'tab:gray',
        'tab:olive',
        'tab:cyan',
    ]

single_char_colours = \
    {
        'b': 'as blue',
        'g': 'as green',
        'r': 'as red',
        'c': 'as cyan',
        'm': 'as magenta',
        'y': 'as yellow',
        'k': 'as black',
        'w': 'as white'
    }

legend_locations = \
    [
        'best',
        'upper right',
        'upper left',
        'lower left',
        'lower right',
        'right',
        'center left',
        'center right',
        'lower center',
        'upper center',
        'center'
    ]


list1 = tab_colours.copy()
list1.insert(0, 'Colours (1/2): ')

list2 = dict_printer(single_char_colours).split('\n').copy()
list2.insert(0, 'Colours (2/2): ')

list3 = legend_locations.copy()
list3.insert(0, 'Legend Locations: ')


allowed_colours = set(tab_colours).union(single_char_colours.keys())
allowed_legend_locations = set(legend_locations)


colour_usage_string = merge_columns(list1, list2)
legend_location_usage_string = list_printer(legend_locations)
