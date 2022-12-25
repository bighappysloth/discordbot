import discord
from discord.ext import commands
from config import __DISCORD_API_KEY__

from pathlib import Path
from typing import List
import datetime


import logging
import traceback 


import io
import re
import pathlib
import argparse
import platform
import sys
import time


import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sympy as sym


from sympy import *
from sympy.core import sympify
from sympy.abc import x


# Bot Modules
import user_configuration
from bot_helpers import *
import latex_to_png
from bot_flags import *


from latex2sympy2 import latex2sympy as latex_to_sympy


"""
List of Commands
plotFunction
matlab2sympy
matlab2latex
latex2sympy
stringnumstring
sandwich
"""


# Command Line Arguments for Function_Plotter
parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='command') # controls the command to use,

plotFunction_parser = subparser.add_parser('plotFunction')

plotFunction_parser.add_argument('-function','--f',
type=str, 
required=True, 
help = 'Function to Plot (Wrap in Quotes)',
dest='function')

plotFunction_parser.add_argument('-xlim','--x', 
type=float, 
nargs=2,
required=False,
help = 'xlimits (optional), default = -10 10',
default = [-10,10],
dest='xlim')

plotFunction_parser.add_argument('-ylim','--y', 
type=float, 
nargs=2,
required=False,
help = 'ylimits (optional), default = min/max f(x)',
dest='ylim')

plotFunction_parser.add_argument('-samples',
'--s', 
type=int, 
required=False,
help = 'Number of Samples (optional), default = 100',
default = 100,
dest='samples')

plotFunction_parser.add_argument('-grid',
'--g', 
type=bool,
required=False,
default=True,
help='Grid (optional), default = on',
dest='grid')

matlab2sympy_parser = subparser.add_parser('matlab2sympy')

matlab2latex_parser = subparser.add_parser('matlab2latex')

latex2sympy_parser = subparser.add_parser('latex2sympy')

stringnumstring_parser = subparser.add_parser('stringnumstring')

matlab2sympy_parser.add_argument('-input','--i',
type=str, 
required=True, 
help = 'MatLab Input',
dest='input')

matlab2latex_parser.add_argument('-input','--i',
type=str, 
required=True, 
help = 'MatLab Input',
dest='input')


latex2sympy_parser.add_argument('-input','--i',
type=str, 
required=True, 
help = 'Latex Input',
dest='input')


# Initialize MatPlotLib
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": "Computer Modern Roman",
    "pgf.rcfonts": False,    # don't setup fonts from rc parameters
    "pgf.preamble": "\n".join([
         #r"\usepackage{url}",            # load additional packages
         #r"\usepackage{unicode-math}",   # unicode math setup
         r"\usepackage{amsmath}",  # serif font via preamble
    ])
    #"text.latexpreamble": r'\usepackage{amsmath}'
})


# def discord_to_args(userLine):



# Custom Method for inline Latex Printing.
async def inline_print(m,use_ln_over_log=True):
    temp = latex(m,mode='inline',ln_notation=use_ln_over_log)
    print(f'inline_print: {temp}')
    return temp


async def gen_plot(args):
    print(f'gen_plot receives the following: {args}')
    print(f'Function: {args.function})')
    myFunction = latex_to_sympy(args.function)
    print(f'Function(Sympy): {myFunction}')
    print(f'xlimits: {args.xlim}')
    
    userFunction = sympify(myFunction, convert_xor=True) # use subs(x,x_i) to evaluate.

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    plt.show(block=False)
    # Plot Title
    # Want to extend this to multiple curves we can plot ont he same figure.
    # How would we scale the axes and domain?
    title_2 = await inline_print(userFunction)
    title_1 = await inline_print(userFunction.doit())
    if isinstance(userFunction,Integral):
        print(f'Integral Instance Detected: {userFunction}')
        if title_1 == title_2: 
            plot_title = 'Plot ' + title_1
        else:
            plot_title = 'Plot ' + title_1 + '='  + title_2
    else:
        plot_title = 'Plot ' + title_1
    
    print(f'Title: {plot_title}')
    ax.set_title(f'{plot_title}')
    ax.grid(visible=args.grid)
    
    
    # If something is an instance of an integral then we will not evaluate it right away but instead calculate it at the last moment.
    

    # Create the linspace array.
    t = np.linspace(args.xlim[0],args.xlim[1],args.samples)
    
    #Substitute Each entry f(t_i) and create new array.
    f_t = np.array([userFunction.doit().subs(x,ti) for ti in t])
    
#   Data arrays for debugging
#   print(f't: {t}')
#   print(f'f(t): {f_t}')

    plot_settings = {
    'color': 'tab:orange',
    'label': r'$f(x)$',
    'linewidth': 2.5,
    }
    ax.plot(t,f_t,**plot_settings)  # Plot some data on the axes.

    ax.set_xlim((args.xlim[0],args.xlim[1])) # default case handled by argparse

    ax.set_ylim(args.ylim[0] if args.ylim else float(f_t.min()), args.ylim[1] if args.ylim else float(f_t.max()))

    # Axes Legend 
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html#matplotlib-axes-axes-legend

    ax.legend(loc='upper right') # apply legend after we are done plotting lines and their labels.
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$y=f(x)$')

    #fig.savefig('function_plot.pdf',transparent=True, backend='pgf')
    
    plot_image_filename = f'{datetime.datetime.now().strftime("Plot %Y-%m-%d at %H.%M.%S.png")}'

    p = Path('.')
    plot_image_path = p/plot_image_filename
    
    print(f'Saving to {plot_image_path}...')
    try:
        fig.savefig(f'{plot_image_path}',transparent=false, backend='pgf',dpi=300)
    except Exception as E:
        return {
            'status': 'failure',
            'reason': E.args
        }
    return {
        'status': 'success',
        'image_path': plot_image_path,
        'plot_titles': [title_1, title_2],
    }

# Bot Subscription to Particular Events
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def time(ctx,* , arg):
    temp = f'{datetime.datetime.now().strftime("Date %Y-%m-%d at %H.%M.%S")}'
    await ctx.send(f'Time is {temp}')
    

@bot.command()
async def plot(ctx, *, flags: plotFunctionFlags):
    
    temp = [r'plotFunction',
    f'-function={flags.function}']

    #The Correct Way to Handle Multiple Arguments
    if flags.xlim: 
        temp.append('-xlim')
        temp.append(flags.xlim.split()[0])
        temp.append(flags.xlim.split()[1])
    if flags.ylim: 
        temp.append('-ylim')
        temp.append(flags.ylim.split()[0])
        temp.append(flags.ylim.split()[1])
    
    if flags.samples: temp.append(f'-samples={flags.samples}')
    if flags.grid!=None: temp.append(f'-grid={str(flags.grid)}')

    await ctx.send(f'plotFunction invoked w/ `{temp}`')
    print(f'PLOTFUNCTION ARRAY: {temp}')
    print(f'args: {parser.parse_args(temp)}')
    result = await gen_plot(parser.parse_args(temp))
    print(f'Image Saved to {result["image_path"]}')
    
    with open(result["image_path"], 'rb') as fp:
        await ctx.send(file=discord.File(fp,f'{result["image_path"]}'))


# For the following three functions, no parsing is done.
# it is simple enough that we do not require any parsers.
@bot.command()
async def matlab2sympy(ctx, *, x: str):
    temp = [r'matlab2sympy']
    temp.append('-input')
    temp.append(x)
    await ctx.send(f'matlab2sympy invoked w/ `{temp}`')
    print(f'matlab2sympy: {temp}')

    z = await matlab_to_sympy(x)
    print(f'matlab2sympy: {x} --> {z}')
    await ctx.send(f'`{z}`') #send result
    

@bot.command()
async def matlab2latex(ctx, *, flags: matlab2latexFlags):
    print(f'matlab2latex executed with {flags.xinput}')
    xprint_args = {}
    
    if flags.matrix_env != None: xprint_args['env'] = flags.matrix_env
    if flags.verbatim != None: xprint_args['verb'] = flags.verbatim
    if flags.title != None: xprint_args['title'] = flags.title
    if flags.latex_mode != None: xprint_args['latex_mode'] = flags.latex_mode
    
    z = await xprint(await matlab_to_sympy(flags.xinput), **xprint_args)
    
    temp = [r'matlab2latex']
    temp.append('-input')
    temp.append(flags.xinput)

    for k in xprint_args: 
        temp.append(k)
        temp.append(xprint_args[k])

    await ctx.send(f'matlab2latex invoked w/ `{temp}`') # debug
    print(f'matlab2latex: {temp}') # debug

    print(f'matlab2latex: {x} --> {z}') #result
    await ctx.send(f'`{z}`') #send result


@bot.command()
async def latex2sympy(ctx, *, flags: latex2sympyFlags):
    temp = [r'latex2sympy']
    temp.append('-input')
    temp.append(flags.xinput)
    await ctx.send(f'latex2sympy invoked w/ `{temp}`')
    print(f'latex2sympy: {temp}')

    z = latex_to_sympy(flags.xinput)
    print(f'latex2sympy: {flags.xinput} --> {z}')
    await ctx.send(f'`{z}`') #send result


# @bot.command()
# async def latex2png(ctx, *, flags: latex2pngFlags):
#     await ctx.send(f'latex2png invoked w/ `{flags.xinput}`')
#     result = await latex_to_png(
#     flags.xinput,
#     tex_mode=flags.latex_mode,
#     alt_mode=flags.alternate,
#     DENSITY=flags.dpi)
#     if result['status'] == 'success':
#         im_location = result['image_path']
#         with open(im_location, 'rb') as fp:
#             await ctx.send(file=discord.File(fp,f'{im_location}'))
#     else:
#         # Error Detected
#         raise commands.CommandError(f'latex2png Error: {result["reason"]}')

"""
latex2png default inline mode
"""
@bot.command(name='t')
async def _make_latex_to_png(ctx, *, z):
    await ctx.send(f'{ctx.author}: TT invoked w/ `{z}`')
    
    result = await latex_to_png.converter(z,tex_mode = 'inline', alt_mode=True,DENSITY=2400)
    
    if result['status'] == 'success':
        im_location = result['image_path']
        with open(im_location, 'rb') as fp:
            await ctx.send(file=discord.File(fp,f'{im_location}'))
    else:
        # Error Detected
        raise commands.CommandError(result["reason"])




# @bot.command()
# async def test(ctx):
#     temp = f'{datetime.datetime.now().strftime("Plot %Y-%m-%d at %H.%M.%S.png")}.png'
#     print(f'test invoked with {temp}')
#     await ctx.send(f'test invoked with {temp}')


@bot.event
async def on_ready():
    print(f"ccE's Discord Bot")
    print(f'Current Time: {current_time()}')
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_command_error(ctx, error):
    z = f'Command Error: `{error}`'
    
    await ctx.send(f'{z}')


# @bot.event
# async def on_message(message):
#     if message.author == bot.user: # Prevent loops
#         return
 
#     # if message.content.startswith(r'function_plot'):
#     #     await message.channel.send('Hello!')
#     #     await bot.process_commands(message)
#     #     return


# Run Bot
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
bot.run(__DISCORD_API_KEY__,log_handler=handler)


# TODO: how to reply to the previous user
# FEATURE: click for latex output.
# REQUIRE: Detection of Edits, and Reactions

# Matrix Converter. Accepts different notation (e,g MatLab Notation)
# Table Maker in Latex
# StringNumString

# TODO Domain Restrictions. for plotFunction
# itemizeMe, enumerateMe
# string num string

# Simplify Function, collect polynomials