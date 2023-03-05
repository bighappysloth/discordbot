import logging

import sympy as sym
from latex2sympy2 import latex2sympy


from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.module_args.latex_args import *

logger = logging.getLogger(__name__)


async def matlab_to_sympy(x):

    mapping = {
        r"\[": "",
        r"\]": "",
        r"\,": "&",
        r";": r"\\" + r"\\",
    }  # each r'\\' is one backslash
    h = RegexReplacer(settings=mapping)
    temp = latex2sympy(h.wrapenv(h.decode(x), "bmatrix"))
    logger.debug(f"matlab2sympy execution: {temp}")
    return temp



sym.init_printing()


async def xprint(m, verb=True, env="regular", latex_mode="inline", title=None):

    """
    Prints Latex from Sympy Inputs based on User Settings. There are two main modes, Matrices and Non-matrices.

    1) Matrices
    env:
        'regular'           bmatrix
        'mini'              bsmallmatrix
        'rounded'           pmatrix
        'mini_rounded'      psmallmatrix
    latex_mode:
        'inline'            adds $[TITLE= ]$,
        'display'           adds or [TITLE: ]\[\],
        'title_display'     adds \[ [TITLE= ]   \] within the display   block.
        'equation'          adds \begin{equation} \end{equation},
        'equation*'         adds \begin{equation*} \end{equation*},
    newline (bool):         whether to add '\n\n' or not at the end.
    verb    (bool):         whether to surround the title in \verb| |
    eval: flag?

    2) Non-matrices

    """

    h = RegexReplacer()

    tex_print_kwargs = {
        "full_prec": False,
        "mat_delim": "",
        "mat_str": matrix_environments[env]
        if env in matrix_environments.keys()
        else matrix_environments["regular"],
        "mode": "plain"
        if latex_mode in {"inline", "title_display", "display"}
        else latex_mode,
        "min": 2,
        "symbol_names": h.latex_symbol_list,
    }

    if not latex_mode in latex_modes:
        raise ValueError(f"Invalid latex_mode {latex_mode}. Allowed: {latex_modes}")

    if isinstance(m, (sym.Matrix, sym.MatrixSymbol)):

        # Here the 'env' argument can be discarded, we only care about the mode inline or display. Equation mode also matters but w will not use it much.

        if not env in matrix_environments:
            raise ValueError(
                f"Invalid env {env}. Allowed: {list(matrix_environments.keys())}"
            )

        z = latex(m, **tex_print_kwargs)

    else:

        z = latex(m, **tex_print_kwargs)

    # Now we (almost) always put the text within the Math Environment, which reads
    # tex_title = \begin{bmatrix} ... \end{bmatrix}
    # except for latex_mode == 'display', where
    # tex_title
    #   \[  \begin{bmatrix} ... \end{bmatrix}  \]

    # Attach verb and text env depending on flags.
    # Checks if title is None. If it is, then do nothing.
    tex_title = (
        (await h.wrap(title, "verb") if verb else await h.wrap(title, "text"))
        if title
        else ""
    )

    # Appends '=' depending on we place the title inside the math env.
    tex_title = (
        (
            tex_title + "="
            if latex_mode in {"inline", "title_display"}
            else await tex_title
        )
        if tex_title
        else ""
    )

    if latex_mode == "inline":
        z = f"${tex_title}{z}$"

    elif latex_mode == "display":
        z = tex_title + r"\[" + z + r"\]"

    elif latex_mode == "title_display":
        z = r"\[" + f"{tex_title}{z}" + r"\]"
    logger.debug(z + h.newline(0, 1))
    return z
