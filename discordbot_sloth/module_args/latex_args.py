from discordbot_sloth.module_args.matplotlib_args import HelperString

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

allowed_env_usage_string = HelperString.dict_printer(matrix_environments)

allowed_latex_modes_usage_string = HelperString.list_printer(list(latex_modes))