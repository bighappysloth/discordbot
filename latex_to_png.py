
#Include tex_fname with .tex extension
# 
import datetime
import shlex
from pathlib import Path
import subprocess
import os
import asyncio

import user_configuration

__TEX_OUT_DIRECTORY__ = \
'latex_out'

COMMAND_PDF_COMPILE = \
'latexmk -quiet -silent -cd -f -xelatex "{0}"'

COMMAND_CLEANUP1 = \
'latexmk -quiet -silent-cd -c "{0}"'# does not remove pdf files

COMMAND_CLEANUP2 = \
'latexmk -quiet -silent -cd -C "{0}"'# removes pdf files as well

COMMAND_PNG_CONVERT = \
'convert -density {0}  -colorspace RGB -alpha opaque -background white  -quality {1} "{2}" "{3}"'

COMMAND_CLEANUP3 = \
'latexmk -c -cd -f {}/'

COMMAND_IMG_CONVERT_WITHTRIM = \
'convert -trim -density {0} -quality {1} "{2}" "{3}"'


TEX_FILE_HEADER = {\
'tight': r'''\documentclass[preview]{standalone}
\usepackage{import}
\import{./}{imports}
\import{./}{engineering_imports} % uncomment if necessary
\begin{document}''',

'regular': r'''\documentclass[preview, border=10pt, 6pt]{standalone}
\usepackage{import}
\import{./}{imports}
\import{./}{engineering_imports} % uncomment if necessary
\begin{document}''',

'wide': r'''\documentclass[preview, border=20pt, 12pt]{standalone}
\usepackage{import}
\import{./}{imports}
\import{./}{engineering_imports} % uncomment if necessary
\begin{document}'''

}

TEX_DELIMITERS = {
'inline': lambda x: '$' + x + '$',
'display': lambda x: r'\[' + x +r'\]'
}

async def run_shell_command(shell_command):

    """
    Runs a shell command with default timeout of 10 seconds,
    Polling Interval 0.5.

    Caller should handle subprocess.TimeoutExpired and subprocess.CalledProcessError
    """
    print(f'Running {shlex.split(shell_command)}...')

    POLLING_INTERVAL = 0.5
    SHELL_TIMEOUT = 10

    process = subprocess.Popen(shlex.split(shell_command)) 

    for i in range(int(SHELL_TIMEOUT / POLLING_INTERVAL)):

        await asyncio.sleep(POLLING_INTERVAL) # polls process every polling interval.
        if process.poll() is not None: break # Finishes before timeout.


    if process.poll() is None: # Does not finish before timeout.
        process.kill()
        raise subprocess.TimeoutExpired(shell_command, SHELL_TIMEOUT, process.stdout, process.stderr)

    if process.poll()==0: return str(process.stdout) #nothing is wrong
        
    raise subprocess.CalledProcessError(process.poll(), shell_command, process.stdout, process.stderr)


def check_dir(dirname):
    if not Path(dirname): Path.mkdir(dirname)


async def converter( userInput, 
                tex_fname=datetime.datetime.now().strftime("Snippet %Y-%m-%d at %H.%M.%S.tex"),
                tex_dir = __TEX_OUT_DIRECTORY__, 
                DENSITY = 1200, 
                QUALITY = 100, 
                framing = 'regular',
                save_pdf = False,
                tex_mode = 'inline'):

    print(f'Converter invoked with args: {DENSITY}, {tex_mode}, {framing}')    
    file_contents = TEX_FILE_HEADER[framing] if TEX_FILE_HEADER.get(framing) else TEX_FILE_HEADER['regular']
    
    if not userInput: userInput = r'\,'

    p = Path('.')
    p = p / tex_dir / tex_fname

    with open(p,'w') as texFile:    
        file_contents = file_contents + '\n' + TEX_DELIMITERS[tex_mode](userInput) + '\n' + r'\end{document}'
        print(f'Writing contents to path: {p}')
        texFile.write(file_contents)
        texFile.flush()
        texFile.close()

    image_fname = tex_fname[:-4] + r'.png'
    pdf_fname = tex_fname[:-4] + r'.pdf'

    image_path = p.parent / image_fname
    pdf_path = p.parent / pdf_fname
    
    try:
        await run_shell_command(COMMAND_PDF_COMPILE.format(p))
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'reason': 'Timeout Exceeded when compiling PDF.'
        }
    except subprocess.CalledProcessError:
        return {
            'status': 'error',
            'reason': 'Failure to compile PDF with xelatex. See log with details.',
            'log_path': p.parent/ str(tex_fname[:-4] + r'.log')
        }

    try:
        await run_shell_command(COMMAND_PNG_CONVERT.format(DENSITY,QUALITY,pdf_path,image_path))
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'reason': 'Timeout Exceeded when converting PDF to PNG'
        }
    except subprocess.CalledProcessError:
        return {
            'status': 'error',
            'reason': 'Failure to convert PDF to PNG'
        }

    # latexmk Cleanup delete all aux files.
    try:
        await run_shell_command(COMMAND_CLEANUP3.format(tex_dir))
        # if save_pdf:
        #     await run_shell_command(COMMAND_CLEANUP1.format(p)) # 
        # else:
        #     await run_shell_command(COMMAND_CLEANUP2.format(p)) #
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'reason': 'Timeout exceeded when performing latexmk cleanup.'
        }
    except subprocess.CalledProcessError:
        return {
            'status' : 'error',
            'reason': 'latexmk cleanup failed.'
        }


    # Return paths, trust on the caller to keep track of whether they used the flag 'save_tex'
    return {
        'status': 'success',
        'image_path': image_path,
        'pdf_path': pdf_path,
        'tex_path': p
    }

    


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coroutine = converter(r'\dfrac{\alpha}{2}',tex_mode='display')
    
    loop.run_until_complete(coroutine)
