import re

from sympy import *
from sympy.abc import epsilon


import logging


logger = logging.getLogger(__name__)


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
                [re.compile(y), settings[k] if k != r"_BACK_SLASH" else settings[k]]
            )

    async def encode(self, x, verbose=False):
        """Encodes any problematic expression by hiding the backslashes and curly braces."""
        temp = x
        if verbose:
            logger.debug(f"fstring (encoder): {x}")
        for filter in self.encode_filters:
            temp = re.sub(*filter, temp)
            # if verbose: logger.debug(f'temp: {temp}')
        return temp

    async def decode(self, x, verbose=False):
        """Decodes using decode_filters."""
        temp = x
        if verbose:
            logger.debug(f"fstring (decoder): {x}")
        for filter in self.decode_filters:
            temp = re.sub(*filter, temp)
            # if verbose: logger.debug(f'temp: {temp}')
        return temp

    async def print_filters(self):
        # Print Filters
        for filter in self.encode_filters:
            logger.debug(*filter)
        for filter in self.decode_filters:
            logger.debug(*filter)

    async def wrap(self, x, env):
        if env == "verb":
            return "\\" + "verb|" + x + "|"
        return "\\" + env + "{" + x + "}"

    async def newline(self, x: int = 1, y: int = 0):
        """
        Returns a newline format suitable for Latex.
        """
        return "\\\\" * x + "\n" * y

    async def wrapenv(self, x, env):
        return "\\" + "begin{" + env + "}" + x + "\\" + "end{" + env + "}"
