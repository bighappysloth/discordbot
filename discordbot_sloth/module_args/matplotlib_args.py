from functools import reduce

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


class HelperString:
    # Prints a list vertically with '\n'
    @staticmethod
    def list_printer(x): return reduce(lambda y, z: y + '\n' + z, x)

    @staticmethod
    def dict_printer(x): return HelperString.list_printer(
        [f'{z}: {x[z]}' for z in x])

    @staticmethod
    def mergeColumns(*args, spacing=4, align='left'):
        """
        Given a list of lists of strings. Print them in columns
        Calculates the maximum width of each column.
        Provides options ot adjust spacing and alignment: 'left' or 'right'.
        """

        M = [L.copy() for L in args]  # copy all columns
        for L in M:
            L.reverse()  # reverse all columns

        M = [
            [L.copy(),
            max([len(x) for x in L])]
            for L in args
        ]

        fmt = {
            'left': lambda r, cell, numspaces: r + cell + ' '*numspaces,
            'right': lambda r, cell, numspaces: r + ' '*numspaces + cell,
        }

        for [a, b] in M:
            a.reverse()

        row_array = []
        while True:
            # While there are still elements to be printed.
            emptyRow = True
            # Print row

            row = ''
            for [a, b] in M:

                # pop if list A is non-empty, else put a blank there.

                if a:
                    temp = a.pop()
                    emptyRow = False
                else:
                    temp = ''

                # calc and add spaces according to how big temp is
                row = fmt[align](row, temp, spacing+b-len(temp))

            row_array.append(row)
            if emptyRow:
                break
        return HelperString.list_printer(row_array)




list1 = tab_colours.copy()
list1.insert(0, 'Colours (1/2): ')

list2 = HelperString.dict_printer(single_char_colours).split('\n').copy()
list2.insert(0, 'Colours (2/2): ')

list3 = legend_locations.copy()
list3.insert(0, 'Legend Locations: ')


allowed_colours = set(tab_colours).union(single_char_colours.keys())
allowed_legend_locations = set(legend_locations)


colour_usage_string = HelperString.mergeColumns(list1, list2)
legend_location_usage_string = HelperString.list_printer(legend_locations)
