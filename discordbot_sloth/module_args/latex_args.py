from discordbot_sloth.helpers.RegexReplacer import *


matrix_environments = {
    "mini": "bsmallmatrix",
    "regular": "bmatrix",
    "rounded": "pmatrix",
    "mini_rounded": "psmallmatrix",
}

latex_modes = {
    "inline",
    "title_display",
    "display",
    "equation",
    "equation*",
}

allowed_env_usage_string = dict_printer(matrix_environments)

allowed_latex_modes_usage_string = list_printer(list(latex_modes))