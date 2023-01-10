from pathlib import Path
import datetime
import logging

import matplotlib.pyplot as plt
import numpy as np

from sympy import *
from sympy.core import sympify
from sympy.abc import x

from latex2sympy2 import latex2sympy as latex_to_sympy
from discordbot_sloth.config import __DATA_PATH__

# Logger
logger = logging.getLogger(__name__)

# Initialize MatPlotLib
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": "Computer Modern Roman",
        "pgf.rcfonts": False,  # don't setup fonts from rc parameters
        "pgf.preamble": "\n".join(
            [
                # r"\usepackage{url}",            # load additional packages
                # r"\usepackage{unicode-math}",   # unicode math setup
                r"\usepackage{amsmath}",  # serif font via preamble
            ]
        )
        # "text.latexpreamble": r'\usepackage{amsmath}'
    }
)


# Custom Method for inline Latex Printing.
async def inline_print(m, use_ln_over_log=True):

    temp = latex(m, mode="inline", ln_notation=use_ln_over_log)
    logger.debug(f"inline_print: {temp}")
    return temp


async def gen_plot(args):
    logger.debug(f"gen_plot receives the following: {args}")
    logger.debug(f"Function: {args.function})")
    myFunction = latex_to_sympy(args.function)
    logger.debug(f"Function(Sympy): {myFunction}")
    logger.debug(f"xlimits: {args.xlim}")

    userFunction = sympify(myFunction, convert_xor=True)  # use subs(x,x_i) to evaluate.

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    plt.show(block=False)
    # Plot Title
    # Want to extend this to multiple curves we can plot ont he same figure.
    # How would we scale the axes and domain?
    title_2 = await inline_print(userFunction)
    title_1 = await inline_print(userFunction.doit())
    if isinstance(userFunction, Integral):
        logger.debug(f"Integral Instance Found: {userFunction}")
        if title_1 == title_2:
            plot_title = "Plot " + title_1
        else:
            plot_title = "Plot " + title_1 + "=" + title_2
    else:
        plot_title = "Plot " + title_1

    logger.debug(f"Title: {plot_title}")
    ax.set_title(f"{plot_title}")
    ax.grid(visible=args.grid)

    # If something is an instance of an integral then we will not evaluate it right away but instead calculate it at the last moment.

    # Create the linspace array.
    t = np.linspace(args.xlim[0], args.xlim[1], args.samples)

    # Substitute Each entry f(t_i) and create new array.
    f_t = np.array([userFunction.doit().subs(x, ti) for ti in t])

    #   Data arrays for debugging
    #   print(f't: {t}')
    #   print(f'f(t): {f_t}')

    plot_settings = {
        "color": "tab:orange",
        "label": r"$f(x)$",
        "linewidth": 2.5,
    }
    ax.plot(t, f_t, **plot_settings)  # Plot some data on the axes.

    ax.set_xlim((args.xlim[0], args.xlim[1]))  # default case handled by argparse

    ax.set_ylim(
        args.ylim[0] if args.ylim else float(f_t.min()),
        args.ylim[1] if args.ylim else float(f_t.max()),
    )

    # Axes Legend
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html#matplotlib-axes-axes-legend

    ax.legend(
        loc="upper right"
    )  # apply legend after we are done plotting lines and their labels.
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y=f(x)$")

    # fig.savefig('function_plot.pdf',transparent=True, backend='pgf')

    plot_image_filename = (
        f'{datetime.datetime.now().strftime("Plot %Y-%m-%d at %H.%M.%S.png")}'
    )

    plot_image_path = __DATA_PATH__ / "plots_out" / plot_image_filename

    logger.debug(f"Saving to {plot_image_path}...")
    try:
        fig.savefig(f"{plot_image_path}", transparent=false, backend="pgf", dpi=300)
    except Exception as E:
        return {"status": "failure", "reason": E.args}
    return {
        "status": "success",
        "image_path": plot_image_path,
        "plot_titles": [title_1, title_2],
    }
