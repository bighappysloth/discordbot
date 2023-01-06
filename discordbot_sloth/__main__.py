import argparse
import datetime
import json
import logging
import sys
from functools import reduce

import discord
from discord.ext import commands
from latex2sympy2 import latex2sympy as latex_to_sympy

from discordbot_sloth.config import __DISCORD_API_KEY__
from discordbot_sloth.discordpy.bot_flags import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.modules.latex_sympy_matlab_conversions import *
from discordbot_sloth.modules.latex_to_png import *
from discordbot_sloth.modules.plotFunction import gen_plot
from discordbot_sloth.user.PseudoPins import *
from discordbot_sloth.user.user_configuration import *

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


stringnumstring_parser = subparser.add_parser("stringnumstring")



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
    


@bot.command()
async def plot(ctx, *, flags: plotFunctionFlags):

    """
        Input to this is horrible and should be fixed.
    """

    temp = [r"plotFunction", flags.function]

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



# simple enough that we do not require any parsers.
@bot.command()
async def matlab2sympy(ctx, *, x: str):
    z = await matlab_to_sympy(x)
    logger.debug(f"matlab2sympy: {x} --> {z}")
    await ctx.reply(f"`{z}`")  # send result


@bot.command(rest_is_raw=True)
async def matlab2latex(ctx, *, arg: str):
    u = str(ctx.author.id)
    """
    If empty argument, then swaps between title and non-title mode.
    """
    logger.debug(f"matlab2latex executed with {arg}")
    
    if not arg:
        """
        Toggle use_title
        """
        
        temp = Configuration(u)

        result = temp.editEntry('xprint_settings.use_title', 
                    not temp.getEntry('xprint_settings.use_title'))
        
        await ctx.reply(f"{result['status']}: {result['msg']}")
        logger.info(f"{result['status']}: {result['msg']}")
    else:
        temp = Configuration(u)
        
        # Now check if use_title is enabled.
        # Split using shlex, because the title can contain spaces.

        xprint_args = {\

        'verb': temp.getEntry('xprint_settings.verb'),
        'env': temp.getEntry('xprint_settings.env'),
        'latex_mode': temp.getEntry('xprint_settings.latex_mode'),
        }
        matlab = arg
        if temp.getEntry('xprint_settings.use_title'):

            split = shlex.split(arg)
            logger.debug(f'split? given \n{split}')
            xprint_args['title'] = split[0]
            matlab = split[1]

        x = await xprint(await matlab_to_sympy(matlab), **xprint_args)

        logger.debug(f"matlab2latex: {arg} --> {x}")  # result
        await ctx.reply(f"`{x}`")  # send result


@bot.command()
async def latex2sympy(ctx, *, z):
    x = latex_to_sympy(z)
    logger.debug(f"latex2sympy: {z} -> {x}")
    await ctx.send(f"`{x}`")  # send result


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
        #print(f"Split: {split}")
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
        logger.info(f"{result['status']}: {result['msg']}")


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
