"""
File to Manage Bot Flags
"""

import discord
from discord.ext import commands

import user_configuration
from bot_helpers import *
import latex_to_png

class plotFunctionFlags(commands.FlagConverter, delimiter=' ', prefix = '-'):
    function: str = commands.flag(name = 'f',
    description='Function to Plot (Do not Wrap in Quotes)')
    
    grid: bool = commands.flag(name='grid', 
    default = True,
    description='Grid (optional), default = on')

    xlim: str = commands.flag(name='xlimits', 
    default = None,
    description='xlimits (optional), default = -10 10') # Works without spaces, i.e # xlim: 10 11 xlim: 12 13
    
    ylim: str = commands.flag(name='ylimits',
    default = None,
    description='ylimits (optional), default = min/max f(x)')
    
    samples: int = commands.flag(name='samples',
    default = None,
    description='Number of Samples (optional), default = 100')


class matlab2latexFlags(commands.FlagConverter, delimiter=' ', prefix = '-'):
    xinput: str = commands.flag(name = 'input',
    description='matlab matrix (input)')

    matrix_env: str = commands.flag(name = 'env',
    description=f'output latex matrix environment {__ALLOWED_MATRIX_ENVIRONMENTS__}',
    default = None) # we let xprint defaults handle this.

    verbatim: bool = commands.flag(name = 'verb',
    description='whether the title is printed in verbatim or not',
    default = True)

    title: str = commands.flag(name = 'title',
    description='title (name) of the matrix',
    default = None)

    latex_mode: str = commands.flag(name = 'mode',
    description=f'output latex mode: {__ALLOWED_LATEX_MODES__}',
    default = None)


class latex2sympyFlags(commands.FlagConverter, delimiter=' ', prefix = '-'):
    xinput: str = commands.flag(name = 'input',
    description='latex (input)')

class latex2pngFlags(commands.FlagConverter, delimiter=' ', prefix = '-'):
    xinput: str = commands.flag(name = 'input',
    description='latex (input)')
    
    latex_mode: str = commands.flag(name = 'mode',
    description=r"'inline' or 'display' math mode. Adds delimiters by default.",
    default = 'inline')

    alternate: bool = commands.flag(name='altmode', 
    default = False,
    description='Alterate Framing (optional), default = off')

    dpi: int = commands.flag(name='dpi',
    default = 1200,
    description='Number of Samples (optional), default = 1200')