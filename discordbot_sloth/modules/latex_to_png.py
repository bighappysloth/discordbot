# Include tex_fname with .tex extension

import asyncio
import datetime
import logging
import shlex
import subprocess

from discordbot_sloth.config import __DATA_PATH__
from discordbot_sloth.helpers.check_dir import *
from discordbot_sloth.helpers.RegexReplacer import *

logger = logging.getLogger(__name__)


__TEX_OUT_DIRECTORY__ = "latex_out"

COMMAND_PDF_COMPILE = (
    'latexmk -quiet -silent -cd -f -interaction=nonstopmode -xelatex -file-line-error "{0}"'
)

COMMAND_CLEANUP1 = 'latexmk -quiet -silent-cd -c "{0}"'  # does not remove pdf files

COMMAND_CLEANUP2 = 'latexmk -quiet -silent -cd -C "{0}"'  # removes pdf files as well

COMMAND_PNG_CONVERT = 'convert -density {0}  -colorspace RGB -alpha opaque -background white  -quality {1} "{2}" "{3}"'

COMMAND_CLEANUP3 = 'latexmk -C -cd -f "{0}"'

COMMAND_IMG_CONVERT_WITHTRIM = 'convert -trim -density {0} -quality {1} "{2}" "{3}"'

__TEX_LOG__ = {
    "start": {
        "in_file": "\n" + r"\typeout{==== LOG FILE START ====}",
        "in_log": r"==== LOG FILE START ====",
        "in_log_2": r"\typeout{==== LOG FILE START ====}",
    },
    "end": {
        "in_file": "\n" + r"\typeout{==== LOG FILE END ====}",
        "in_log": r"==== LOG FILE END ====",
        "in_log_2": r"\typeout{==== LOG FILE END ====}",
    },
}


TEX_FILE_HEADER = {
    "tight": r"""\documentclass[preview]{standalone}
\usepackage{import}
\import{./}{imports}
\import{./}{engineering_imports} % uncomment if necessary
\begin{document}""",
    "regular": r"""\documentclass[preview, border=10pt, 6pt]{standalone}
\usepackage{import}
\import{./}{imports}
\import{./}{engineering_imports} % uncomment if necessary
\begin{document}""",
    "wide": r"""\documentclass[preview, border=20pt, 12pt]{standalone}
\usepackage{import}
\import{./}{imports}
\import{./}{engineering_imports} % uncomment if necessary
\begin{document}""",
}

TEX_DELIMITERS = {
    "inline": lambda x: "$" + x + "$",
    "display": lambda x: r"\[" + x + r"\]",
    "raw": lambda x: x,
}

"""
Check Directory Exists
"""
check_dir(__DATA_PATH__ / __TEX_OUT_DIRECTORY__)


def return_latex_log(log_location: Path):
    """Returns a cropped latex log given log location

    Args:
        log_location (Path): path to log

    Returns:
        str: multi-line string.
    """
    with log_location.open("r") as log_file:
        temp = log_file.readlines()

        z = [a.strip() for a in temp]  # remove whitespace \n and \t

        
        
        i = 0
        while not z[i].startswith(r"./Snipp"):
            i = i + 1
        num_lines_to_dump = 3
        end = min(i + num_lines_to_dump, len(z))
        z = z[i:end]
        return list_printer(z)


async def run_shell_command(shell_command):

    """
    Runs a shell command with default timeout of 10 seconds,
    Polling Interval 0.5.

    Caller should handle subprocess.TimeoutExpired and subprocess.CalledProcessError
    """
    logger.debug(f"Running {shlex.split(shell_command)}...")

    POLLING_INTERVAL = 0.5
    SHELL_TIMEOUT = 10

    process = subprocess.Popen(shlex.split(shell_command))

    for i in range(int(SHELL_TIMEOUT / POLLING_INTERVAL)):

        # polls process every polling interval.
        await asyncio.sleep(POLLING_INTERVAL)
        if process.poll() is not None:
            break  # Finishes before timeout.

    if process.poll() is None:  # Does not finish before timeout.
        process.kill()
        raise subprocess.TimeoutExpired(
            shell_command, SHELL_TIMEOUT, process.stdout, process.stderr
        )

    if process.poll() == 0:
        return str(process.stdout)  # nothing is wrong

    raise subprocess.CalledProcessError(
        process.poll(), shell_command, process.stdout, process.stderr
    )


async def latex_to_png_converter(
    userInput,
    tex_fname=datetime.datetime.now().strftime("Snippet %Y-%m-%d at %H.%M.%S.tex"),
    tex_dir=__TEX_OUT_DIRECTORY__,
    DENSITY=1200,
    QUALITY=100,
    framing="regular",
    save_pdf=False,
    tex_mode="inline",
):

    logger.debug(f"Converter invoked with args: {DENSITY}, {tex_mode}, {framing}")
    file_contents = (
        TEX_FILE_HEADER[framing]
        if TEX_FILE_HEADER.get(framing)
        else TEX_FILE_HEADER["regular"]
    )

    if not userInput:
        userInput = r"\,"

    p = __DATA_PATH__ / tex_dir / tex_fname

    with open(p, "w") as texFile:
        file_contents = (
            file_contents
            + "\n\n"
            + __TEX_LOG__["start"]["in_file"]
            + TEX_DELIMITERS[tex_mode](userInput)
            + "\n"
            + __TEX_LOG__["end"]["in_file"]
            + r"\end{document}"
        )
        logger.debug(f"Writing contents to path: {p}")
        texFile.write(file_contents)
        texFile.flush()
        texFile.close()

    image_fname = tex_fname[:-4] + r".png"
    pdf_fname = tex_fname[:-4] + r".pdf"

    image_path = p.parent / image_fname
    pdf_path = p.parent / pdf_fname

    tex_log = {}

    try:
        logger.debug(f"latex_to_png shell: {COMMAND_PDF_COMPILE.format(p)}")
        await run_shell_command(COMMAND_PDF_COMPILE.format(p))
    except subprocess.TimeoutExpired:
        return {"status": "error", "reason": "Timeout Exceeded when compiling PDF."}
    except subprocess.CalledProcessError:  # try to force it
        print('Return code 1')
        log_location = __DATA_PATH__ / tex_dir / Path(str(tex_fname[:-4]) + r".log")
        z = return_latex_log(log_location)

        # Now attempt to fetch image.
        
        tex_log["log"] = z
        tex_log["log_path"] = log_location

    finally:

        try:
            await run_shell_command(
                COMMAND_PNG_CONVERT.format(DENSITY, QUALITY, pdf_path, image_path)
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "reason": "Timeout Exceeded when converting PDF to PNG",
                "image_path": str(image_path) if Path(image_path).exists() else None,
            }
        except subprocess.CalledProcessError:
            return {
                "status": "error",
                "reason": "Failure to convert PDF to PNG",
                "image_path": str(image_path) if Path(image_path).exists() else None,
            }

        # latexmk Cleanup delete all aux files.
        try:
            # cleans up the parent folder
            
            clean_location = str(pdf_path.resolve())
            await run_shell_command(COMMAND_CLEANUP3.format(clean_location))

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "msg": "Timeout exceeded when performing latexmk cleanup.",
            }
        except subprocess.CalledProcessError:
            return {
                "status": "failure",
                "msg": "latexmk cleanup failed.",
                "image_path": str(image_path) if Path(image_path).exists() else None,
            }

        # Return paths, trust on the caller to keep track of whether they used the flag 'save_tex'
        if not tex_log.get("log"):
            return {
                "status": "success",
                "image_path": str(image_path),
                "pdf_path": pdf_path,
                "tex_path": p,
            }
        else:
            return {
                "status": "failure",
                "reason": "Failure to compile PDF with xelatex. See log with details.",
                "image_path": str(image_path),
                "log": tex_log["log"],
                "log_path": tex_log["log_path"],
            }


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    coroutine = latex_to_png_converter(r"\dfrac{\alpha}{2}", tex_mode="display")

    loop.run_until_complete(coroutine)
