import re

import sympy as sym
from sympy import *
from sympy.abc import epsilon

import numpy as np

import datetime


from latex2sympy2 import latex2sympy

__ALLOWED_MATRIX_ENVIRONMENTS__ = {'mini': 'bsmallmatrix',
    'regular': 'bmatrix',
    'rounded': 'pmatrix',
    'mini_rounded': 'psmallmatrix'
    }

__ALLOWED_LATEX_MODES__ = {'inline', 
'title_display',
'display',
'equation',
'equation*'}


def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d at %H.%M.%S")

class Helper_fStrings:
    """
    Replace stings given dictionary, supports encoding and decoding methods.
    """

    # use with latex(epsilon,symbol_names={epsilon: r'\varepsilon'})
    latex_symbol_list={epsilon: r'\varepsilon'}

    replacements = {\
    '_LEFT_CURLY':      '' + r'{',
    '_RIGHT_CURLY':     '' + r'}',
    '_BACK_SLASH':      '\\' + '\\'
    }

    #TODO: Keys to encode and decode
    #It is different.

    # build encoding and decoding filters
    def __init__(self, settings=replacements):
        
        self.encode_filters = []
        self.decode_filters = []
        for k in settings:
            
            y = '('+settings[k]+r')'

            self.encode_filters.append([re.compile(y), k])

            y = '(' + k + ')'

            self.decode_filters.append([re.compile(y),settings[k] if k!= r'_BACK_SLASH' else settings[k]])

    
    async def encode(self, x, verbose = False):
        """Encodes any problematic expression by hiding the backslashes and curly braces."""
        temp = x
        if verbose: print(f'fstring (encoder): {x}')
        for filter in self.encode_filters: 
            temp = re.sub(*filter, temp)
            #if verbose: print(f'temp: {temp}')
        return temp


    async def decode(self, x, verbose = False):
        """Decodes using decode_filters."""
        temp = x
        if verbose: print(f'fstring (decoder): {x}')
        for filter in self.decode_filters: 
            temp = re.sub(*filter, temp)
            #if verbose: print(f'temp: {temp}')
        return temp
        
        
    async def print_filters(self):
        # Print Filters
        for filter in self.encode_filters: print(*filter)
        for filter in self.decode_filters: print(*filter)

    
    async def wrap(self, x, env):
        if env == 'verb':
            return '\\' + 'verb|' + x + '|'
        return '\\' + env + '{' + x + '}'
    

    async def newline(self, x: int=1, y: int=0):
        """
        Returns a newline format suitable for Latex.
        """
        return '\\\\'*x + '\n'*y

    async def wrapenv(self,x,env):
        return '\\' + 'begin{' + env + '}' + x + '\\' + 'end{' + env + '}'


async def matlab_to_sympy(x):

    mapping = {\
    r'\[': '',
    r'\]': '',
    r'\,': '&',
    r';': r'\\' +r'\\'
    } #each r'\\' is one backslash
    h = Helper_fStrings(settings = mapping)
    temp = latex2sympy(await h.wrapenv(await h.decode(x), 'bmatrix'))
    print(f'matlab2sympy execution: {temp}')
    return temp


sym.init_printing() 

async def xprint(m, verb=True, env='regular',latex_mode = 'inline', title=None):
    """Prints Latex from Sympy Inputs based on User Settings. There are two main modes, Matrices and Non-matrices. 
    
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
    
    h = Helper_fStrings()
    
    tex_print_kwargs = {'full_prec':False, 
        'mat_delim':'',
        'mat_str':__ALLOWED_MATRIX_ENVIRONMENTS__[env] if env in __ALLOWED_MATRIX_ENVIRONMENTS__.keys() else __ALLOWED_MATRIX_ENVIRONMENTS__['regular'],
        'mode':'plain' if latex_mode in {'inline', 'title_display','display'} else latex_mode,
        'min':2,
        'symbol_names': h.latex_symbol_list}


    if not latex_mode in __ALLOWED_LATEX_MODES__:
            raise ValueError(f'Invalid latex_mode {latex_mode}. Allowed: {__ALLOWED_LATEX_MODES__}')
    

    if isinstance(m,(sym.Matrix,sym.MatrixSymbol)):

        # Here the 'env' argument can be discarded, we only care about the mode inline or display. Equation mode also matters but w will not use it much.
        
            
        if not env in __ALLOWED_MATRIX_ENVIRONMENTS__:
            raise ValueError(f'Invalid env {env}. Allowed: {list(__ALLOWED_MATRIX_ENVIRONMENTS__.keys())}')

        #print(h.wrap(f'\'env\'={env} valid: {env in __ALLOWED_MATRIX_ENVIRONMENTS__}','verb'), end=h.newline() + '\n')

        z = sym.printing.latex(m, **tex_print_kwargs)

    else:

        z = sym.printing.latex(m, **tex_print_kwargs)
    
    # Now we (almost) always put the text within the Math Environment, which reads
    # tex_title = \begin{bmatrix} ... \end{bmatrix}
    # except for latex_mode == 'display', where
    # tex_title
    #   \[  \begin{bmatrix} ... \end{bmatrix}  \]
    

    # Attach verb and text env depending on flags.
    # Checks if title is None. If it is, then do nothing.
    tex_title = (await h.wrap(title,'verb') if verb else await h.wrap(title,'text')) if title else ''
    
    # Appends '=' depending on we place the title inside the math env.
    tex_title = (tex_title + '=' if latex_mode in {'inline', 'title_display'} else await tex_title) if tex_title else ''
    
    if latex_mode == 'inline': z = f'${tex_title}{z}$'
        
    elif latex_mode == 'display': z = tex_title + '\[' + z + '\]'
        
    elif latex_mode == 'title_display': z =  '\[' + f'{tex_title}{z}' + '\]'        
    print(z+await h.newline(0,1))
    return z