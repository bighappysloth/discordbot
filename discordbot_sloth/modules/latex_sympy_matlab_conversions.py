import logging
import re
from functools import reduce
import sympy as sym
from latex2sympy2 import latex2sympy

from discordbot_sloth.module_args.latex_args import matrix_environments
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.module_args.latex_args import *

logger = logging.getLogger(__name__)


async def matlab_to_sympy(x):

    mapping = {
        r"\[": "",
        r"\]": "",
        r"\,": "&",
        r";": r"\\" + r"\\" + r" ",
    }  # each r'\\' is one backslash
    h = RegexReplacer(settings=mapping)
    temp = latex2sympy(h.wrapenv(h.decode(x), "bmatrix"))
    logger.debug(f"matlab2sympy execution: {temp}")
    return temp



# def matrix_to_latex_v2(matrix_string):
#     # Extract matrix and vector substrings
#     regex = r"\[([^]]+)\]\[([^]]+)\]"
#     match = re.search(regex, matrix_string)
#     matrix_substr = match.group(1)
#     vector_substr = match.group(2)

#     # Convert matrix substring to LaTeX
#     matrix_str = matrix_substr.replace(";", " \\\\\n")
#     matrix_str = matrix_str.replace(",", " &")
#     matrix_str = "\\begin{bmatrix}\n" + matrix_str + "\n\\end{bmatrix}"

#     # Convert vector substring to LaTeX
#     vector_str = vector_substr.replace(",", " \\\\\n")
#     vector_str = "\\begin{bmatrix}\n" + vector_str + "\n\\end{bmatrix}"

#     # Combine matrix and vector LaTeX strings
#     latex_str = matrix_str + vector_str

#     return latex_str


def matlab_to_latex_matrices(s, env, compact):
    
    entries_to_latex = lambda entries, environment = 'bmatrix', compact = True: (f'\\begin{{{environment}}}\n' + ' \\\\ \n'.join([' & '.join(row) for row in entries]) + f'\n\\end{{{environment}}}').replace('\n', '' if compact else '\n') 
    
    def extract_matrices(s):
        square_pattern = r'\[(.*?)\]'
        return re.findall(square_pattern, s)

    def extract_entries(m):
        temp = m.lstrip('[').lstrip().rstrip(']').rstrip().split(';') # Removes whitepsace and splits by rows.
        temp = [[entry.lstrip().rstrip() for entry in row.split(',')] for row in temp]
        return temp
    
    # Extract all Matrices
    M = extract_matrices(s)
    M = [extract_entries(m) for m in M] # Extract individual entries
    M = [entries_to_latex(entries, environment = matrix_environments[env], compact = compact) for entries in M]
    return list_printer(M) if not compact else ''.join(M)



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
        'nothing'           adds nothing.
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
        if latex_mode in {"inline", "title_display", "display", "nothing"}
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
        z = tex_title + r"\[" + '\n\t' + z + '\n' + r"\]"

    elif latex_mode == "title_display":
        z = r"\[" + '\n\t' +f"{tex_title}{z}" + '\n' +r"\]"
    logger.debug(z + h.newline(0, 1))
    return z
