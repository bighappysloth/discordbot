import logging

import asyncio
from pathlib import Path

from sympy import *
from sympy.abc import epsilon
from functools import reduce

import re

logger = logging.getLogger(__name__)
list_printer = lambda x: reduce(lambda a, b: a + '\n' + b,x) if x else ''
dict_printer = lambda x: list_printer([f'{z}: {x[z]}' for z in x]) if x else ''

class RegexReplacer:
    """
    Replace stings given dictionary, supports encoding and decoding methods.
    """

    # use with latex(epsilon,symbol_names={epsilon: r'\varepsilon'})
    latex_symbol_list = {epsilon: r"\varepsilon"}

    replacements = {
        "_LEFT_CURLY": "" + r"{",
        "_RIGHT_CURLY": "" + r"}",
        "_BACK_SLASH": "\\" + "\\",
    }

    # TODO: Keys to encode and decode
    # It is different.

    # build encoding and decoding filters
    def __init__(self, settings=replacements):

        self.encode_filters = []
        self.decode_filters = []
        for k in settings:

            y = "(" + settings[k] + r")"

            self.encode_filters.append([re.compile(y), k])

            y = "(" + k + ")"

            self.decode_filters.append(
                [re.compile(y), settings[k] if k !=
                 r"_BACK_SLASH" else settings[k]]
            )

    def encode(self, x, verbose=True):
        """Encodes any problematic expression by hiding the backslashes and curly braces."""
        temp = x
        if verbose:
            logger.debug(f"fstring (encoder): {x}")
        for filter in self.encode_filters:
            temp = re.sub(*filter, temp)
            # if verbose: logger.debug(f'temp: {temp}')
        return temp

    def decode(self, x, verbose=True):
        """Decodes using decode_filters."""
        temp = x
        if verbose:
            logger.debug(f"fstring (decoder): {x}")
        for filter in self.decode_filters:
            temp = re.sub(*filter, temp)
            # if verbose: logger.debug(f'temp: {temp}')
        return temp

    def print_filters(self):
        # Print Filters
        for filter in self.encode_filters:
            logger.debug(*filter)
        for filter in self.decode_filters:
            logger.debug(*filter)

    def wrap(self, x, env):
        if env == "verb":
            return "\\" + "verb|" + x + "|"
        return "\\" + env + "{" + x + "}"

    def newline(self, x: int = 1, y: int = 0):
        """
        Returns a newline format suitable for Latex.
        """
        return "\\\\" * x + "\n" * y

    def wrapenv(self, x, env):
        return "\\" + "begin{" + env + "}" + x + "\\" + "end{" + env + "}"




def merge_columns(*args, spacing=4, align='left'):
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
    return list_printer(row_array)

