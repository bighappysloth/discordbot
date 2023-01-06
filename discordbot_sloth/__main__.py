import discord
from discord.ext import commands


import datetime
import logging
import argparse
import sys
import json
from functools import reduce

from latex2sympy2 import latex2sympy as latex_to_sympy

from discordbot_sloth.config import __DISCORD_API_KEY__
from discordbot_sloth.discordpy.bot_flags import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.modules.plotFunction import gen_plot
from discordbot_sloth.modules.latex_sympy_matlab_conversions import *
from discordbot_sloth.modules.latex_to_png import *
from discordbot_sloth.user.user_configuration import *
from discordbot_sloth.user.PseudoPins import *
from discordbot_sloth.modules.latex_to_png import *


__STAR_EMOJI__ = "\U00002B50"


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
subparser = parser.add_subparsers(dest="command")  # controls the command to use,

plotFunction_parser = subparser.add_parser("plotFunction")

plotFunction_parser.add_argument(
    "-function",
    "--f",
    type=str,
    required=True,
    help="Function to Plot (Wrap in Quotes)",
    dest="function",
)

plotFunction_parser.add_argument(
    "-xlim",
    "--x",
    type=float,
    nargs=2,
    required=False,
    help="xlimits (optional), default = -10 10",
    default=[-10, 10],
    dest="xlim",
)

plotFunction_parser.add_argument(
    "-ylim",
    "--y",
    type=float,
    nargs=2,
    required=False,
    help="ylimits (optional), default = min/max f(x)",
    dest="ylim",
)

plotFunction_parser.add_argument(
    "-samples",
    "--s",
    type=int,
    required=False,
    help="Number of Samples (optional), default = 100",
    default=100,
    dest="samples",
)

plotFunction_parser.add_argument(
    "-grid",
    "--g",
    type=bool,
    required=False,
    default=True,
    help="Grid (optional), default = on",
    dest="grid",
)

matlab2sympy_parser = subparser.add_parser("matlab2sympy")

matlab2latex_parser = subparser.add_parser("matlab2latex")

latex2sympy_parser = subparser.add_parser("latex2sympy")

stringnumstring_parser = subparser.add_parser("stringnumstring")

mt_parser = subparser.add_parser("mt")
mt_parser.add_argument("xinput")  # positional
mt_parser.add_argument("-m", action="store_true")  # store true mode

matlab2sympy_parser.add_argument(
    "-input", "--i", type=str, required=True, help="MatLab Input", dest="input"
)

matlab2latex_parser.add_argument(
    "-input", "--i", type=str, required=True, help="MatLab Input", dest="input"
)


latex2sympy_parser.add_argument(
    "-input", "--i", type=str, required=True, help="Latex Input", dest="input"
)


# Bot Subscription to Particular Events
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.dm_reactions = True
intents.dm_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def time(ctx):
    temp = f'{datetime.datetime.now().strftime("Date %Y-%m-%d at %H.%M.%S")}'

    # temp = json.dumps(result,sort_keys=True,indent=4)
    # print(f'{temp}')
    print(f"reference? {ctx.message.reference}")
    await ctx.send(f"Time: {current_time()}")
    await ctx.send(f"{temp}")
    # emoji = '\U00002B50'
    # await ctx.message.add_reaction(emoji)


@bot.command()
async def plot(ctx, *, flags: plotFunctionFlags):

    temp = [r"plotFunction", f"-function={flags.function}"]

    # The Correct Way to Handle Multiple Arguments
    if flags.xlim:
        temp.append("-xlim")
        temp.append(flags.xlim.split()[0])
        temp.append(flags.xlim.split()[1])
    if flags.ylim:
        temp.append("-ylim")
        temp.append(flags.ylim.split()[0])
        temp.append(flags.ylim.split()[1])

    if flags.samples:
        temp.append(f"-samples={flags.samples}")
    if flags.grid != None:
        temp.append(f"-grid={str(flags.grid)}")

    await ctx.send(f"plot invoked w/ `{temp}`")

    logger.debug(f"plot raw_args {temp}")
    logger.debug(f"plot parsed_args: {parser.parse_args(temp)}")
    result = await gen_plot(parser.parse_args(temp))

    print(f'Image Saved to {result["image_path"]}')

    with open(result["image_path"], "rb") as fp:
        await ctx.send(file=discord.File(fp, f'{result["image_path"]}'))


# For the following three functions, no parsing is done.
# it is simple enough that we do not require any parsers.
@bot.command()
async def matlab2sympy(ctx, *, x: str):
    temp = [r"matlab2sympy"]
    temp.append("-input")
    temp.append(x)
    await ctx.send(f"matlab2sympy invoked w/ `{temp}`")
    print(f"matlab2sympy: {temp}")

    z = await matlab_to_sympy(x)
    print(f"matlab2sympy: {x} --> {z}")
    await ctx.send(f"`{z}`")  # send result


@bot.command()
async def matlab2latex(ctx, *, flags: matlab2latexFlags):
    logger.debug(f"matlab2latex executed with {flags.xinput}")
    xprint_args = {}

    if flags.matrix_env != None:
        xprint_args["env"] = flags.matrix_env
    if flags.verbatim != None:
        xprint_args["verb"] = flags.verbatim
    if flags.title != None:
        xprint_args["title"] = flags.title
    if flags.latex_mode != None:
        xprint_args["latex_mode"] = flags.latex_mode

    z = await xprint(await matlab_to_sympy(flags.xinput), **xprint_args)

    temp = [r"matlab2latex"]
    temp.append("-input")
    temp.append(flags.xinput)

    for k in xprint_args:
        temp.append(k)
        temp.append(xprint_args[k])

    await ctx.send(f"matlab2latex invoked w/ `{temp}`")  # debug
    logger.debug(f"matlab2latex: {temp}")  # debug

    logger.debug(f"matlab2latex: {flags.xinput} --> {z}")  # result
    await ctx.send(f"`{z}`")  # send result


@bot.command()
async def latex2sympy(ctx, *, flags: latex2sympyFlags):
    temp = [r"latex2sympy"]
    temp.append("-input")
    temp.append(flags.xinput)
    await ctx.send(f"latex2sympy invoked w/ `{temp}`")
    logger.debug(f"latex2sympy: {temp}")

    z = latex_to_sympy(flags.xinput)
    logger.debug(f"latex2sympy: {flags.xinput} --> {z}")
    await ctx.send(f"`{z}`")  # send result


"""
latex2png default inline mode
"""


@bot.command(name="t")
async def _make_latex_to_png(ctx, *, z):
    await ctx.reply(f"Generating Image from `{z}`")

    Config = Configuration(str(ctx.author.id))

    result = await latex_to_png_converter(
        z,
        DENSITY=Config.getEntry("png_dpi")["msg"],
        tex_mode=Config.getEntry("latex_mode")["msg"],
        framing=Config.getEntry("framing")["msg"],
    )

    if result["status"] == "success":
        im_location = result["image_path"]
        with open(im_location, "rb") as fp:
            await ctx.reply(file=discord.File(fp, f"{im_location}"))
    else:
        # Error Detected
        raise commands.CommandError(result["msg"])


@bot.command(name="defaults")
async def _view_defaults(ctx):
    # Forget about using Flags, let us try manual parsing with shell
    # No flags needed

    result = viewFullUserConfig(__DEFAULT_USER__)

    if result["status"] == "success":
        await ctx.reply(f"Configuration Options (defaults):\n```{result['msg']}```")
    else:
        await ctx.reply(f"`{result['status']}: {result['msg']}`")
        logger.warning(f"`{result['status']}: {result['msg']}`")


@bot.command(name="config", rest_is_raw=True)
async def _edit_config(ctx, *, arg: str):

    u = str(ctx.author.id)

    if not arg:
        """
        If the user invokes with empty arguments, we show them their own configuration.
        """
        logger.info("No args detected")
        uc = Configuration(u)
        print(f"UC: {uc}")
        await ctx.reply(
            f"{ctx.author.name}'s config:\n```{json.dumps(Configuration(u).settings,sort_keys=True,indent=4)}```"
        )

    else:
        split = arg.split(" ")
        print(f"Split: {split}")
        split = split[1:]
        if len(split) == 1:
            raise commands.CommandError(
                f'!config [selected_option] [new_value], "new_value" is missing.'
            )
        selected_option = split[0]
        new_value = reduce((lambda y, z: y + " " + z), split[1:])

        temp = Configuration(u)
        result = temp.editEntry(selected_option, new_value)

        await ctx.reply(f"{result['status']}: {result['msg']}")


@bot.command(name="restore")
async def _restore_config(ctx):
    u = str(ctx.author.id)
    Configuration.restoreUserConfig(u)
    await ctx.reply(f"Restored {ctx.author.name}'s config to defaults.")
    logger.info(f"Restored {ctx.author.name}'s config to defaults.")


@bot.command(name="pins")
async def _get_pins(ctx):
    u = str(ctx.author.id)
    temp = await UserPins.get_pins(u, bot)
    s = json.dumps(temp, indent=4, sort_keys=True)
    await ctx.reply(s)
    logger.debug(s)


@bot.event
async def on_ready():
    logger.info(f"ccE's Discord Bot")
    logger.info(f"Current Time: {current_time()}")
    logger.info("We have logged in as {0.user}".format(bot))


# @bot.event
# async def on_command_error(ctx, error):
#     z = f'Command Error: `{error}`'

#     await ctx.send(f'{z}')
#     logger.warning(f'{z}, {error.args} {type(error)}')


@bot.event
async def on_command(ctx):
    fulluser = f"{ctx.author} -> {ctx.author.id}"

    logger.info(f'{ctx.author} invoked "{ctx.command}" w/ args {ctx.args[1:]}.')
    logger.debug(f"{fulluser}")


@bot.event
async def on_command_completion(ctx):
    """
    Increments the user's config.usage and config.last_used.
    """
    userid = str(ctx.author.id)
    Configuration.incrementUserConfig(str(userid))


@bot.event
async def on_message_edit(before, after):
    logger.info(f"Edit Detected: {before} -> {after}")


# @bot.event
# async def on_reaction_add(reaction, user):
#     logger.info(f'Reaction Detected: {reaction.Message}, by {user}')


@bot.event
async def on_raw_reaction_add(payload):

    if payload.emoji.name == __STAR_EMOJI__:
        """
        Record the channel, message ID. And the pinning user, and
        passes to PseudoPins
        """
        logger.debug(f"Star Emoji Reaction detected wtih {payload}")

        add_pin_args = {
            "user": str(payload.user_id),
            "payload": {
                "channel_id": str(payload.channel_id),
                "message_id": str(payload.message_id),
                "date": current_time(),
                "unix_date": epoch_delta_milliseconds(),
            },
            "bot": bot,
        }
        # logger.debug(f'add_pin_args: {add_pin_args}')
        logger.info(f'Pinning User: {add_pin_args["user"]}')
        result = await UserPins.add_pin(**add_pin_args)
        # logger.debug(f'pinning_result: {json.dumps(result,sort_keys=True,indent=4)}')


@bot.event
async def on_raw_reaction_remove(payload):
    logger.info(f"Raw Reaction Removed: {payload}")


@bot.event
async def on_raw_message_edit(payload):
    logger.info(f"Raw Message Edit: {payload}")


# Run Bot
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setLevel(logging.DEBUG)
handler_formatting = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler_stdout.setFormatter(handler_formatting)

logger.addHandler(handler_stdout)

handler_filelog = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w"
)
bot.run(__DISCORD_API_KEY__, log_handler=handler_filelog)


# TODO: how to reply to the previous user DONE
# FEATURE: click for latex output (REACTION)
# REQUIRE: Detection of Edits, and Reactions (EDITS)

# Matrix Converter. Accepts different notation (e,g MatLab Notation) (DONE)
# Table Maker in Latex (DONE)
# StringNumString

# TODO Domain Restrictions. for plotFunction
# itemizeMe, enumerateMe
# string num string (deferred)

# TODO Pinbot, Pseudo Pins. Done
# TODO Add VIP List
# TODO Add feature to remove pins
# TODO Add workbook area

# Simplify Function, collect polynomials
