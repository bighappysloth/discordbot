from discordbot_sloth.module_args.matplotlib_args import HelperString

__ALLOWED_MATRIX_ENVIRONMENTS__ = {
    "mini": "bsmallmatrix",
    "regular": "bmatrix",
    "rounded": "pmatrix",
    "mini_rounded": "psmallmatrix",
}

__ALLOWED_LATEX_MODES__ = {
    "inline",
    "title_display",
    "display",
    "equation",
    "equation*",
}

allowed_env_usage_string = HelperString.dict_printer(__ALLOWED_MATRIX_ENVIRONMENTS__)

allowed_latex_modes_usage_string = HelperString.list_printer(list(__ALLOWED_LATEX_MODES__))