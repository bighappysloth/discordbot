import argparse
import datetime
import json
import logging
import signal
import sys
from functools import reduce

import discord
from discord.ext import commands
from latex2sympy2 import latex2sympy as latex_to_sympy

from discordbot_sloth.config import __DISCORD_API_KEY__
from discordbot_sloth.discordpy.bot_flags import *
from discordbot_sloth.helpers.emoji_defaults import *
from discordbot_sloth.helpers.EmojiReactor import react_to_message
from discordbot_sloth.helpers.RegexReplacer import *
from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.modules.latex_sympy_matlab_conversions import *
from discordbot_sloth.modules.latex_to_png import *
from discordbot_sloth.modules.plotFunction import gen_plot
from discordbot_sloth.StateLoader import load_states
from discordbot_sloth.user.PseudoPins import message_identifier
from discordbot_sloth.user.StarredMessage import StarredMessage
from discordbot_sloth.user.State import State
from discordbot_sloth.user.TrackedPanels import (
    LatexImage,
    ParrotMessage,
    PinPanel,
    ShowPinsPanel,
)
from discordbot_sloth.user.user_configuration import *

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
    filename='discord.log', encoding="utf-8", mode="w"
)

def _terminate_bot(signal, frame):
    logger.debug(f"Terminating bot: {str(bot.user.id)}")
    

    for (u, s) in bot.states.items():
        logger.debug(f'Saving user {u}')
        s.save()

    logger.debug("Saving...")

    sys.exit(0)


signal.signal(signal.SIGINT, _terminate_bot)

# Bot Subscription to Particular Events
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.dm_reactions = True
intents.dm_messages = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.run(__DISCORD_API_KEY__, log_handler=handler_filelog)


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


@bot.event
async def on_ready():
    logger.info(f"ccE's Discord Bot")
    logger.info(f"Current Time: {current_time()}")
    bot.states = load_states(bot)
    logger.info("We have logged in as {0.user}".format(bot))


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
    if flags.grid is not None:
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

        result = temp.editEntry(
            "xprint_settings.use_title", not temp.getEntry("xprint_settings.use_title")
        )

        await ctx.reply(f"{result['status']}: {result['msg']}")
        logger.info(f"{result['status']}: {result['msg']}")
    else:
        temp = Configuration(u)

        # Now check if use_title is enabled.
        # Split using shlex, because the title can contain spaces.

        xprint_args = {
            "verb": temp.getEntry("xprint_settings.verb"),
            "env": temp.getEntry("xprint_settings.env"),
            "latex_mode": temp.getEntry("xprint_settings.latex_mode"),
        }
        matlab = arg
        if temp.getEntry("xprint_settings.use_title"):

            split = shlex.split(arg)
            logger.debug(f"split? given \n{split}")
            xprint_args["title"] = split[0]
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


@bot.command(name="t", rest_is_raw=True)
async def _make_latex_to_png(ctx, *, z):

    # Send Initial Reply
    previous = await ctx.reply(f"Making Latex...")

    # Get Username
    u = str(ctx.author.id)

    # Get User State with init_new for regsitration.
    s = bot.states.get(u)
    if s is None:
        bot.states[u] = State(u, bot)
        s = bot.states[u]
        logger.debug(f"Registering {u}")

    identifier = message_identifier( 
                                    channel_id=ctx.channel.id, 
                                    message_id=ctx.message.id
    )
        
    x = LatexImage(channel_id=previous.channel.id, message_id=previous.id, user=u)


    s.state[identifier] = x
    await x.on_edit(z, bot)


@bot.command(name="defaults")
async def _view_defaults(ctx):
    # Forget about using Flags, let us try manual parsing with shell
    # No flags needed

    result = viewFullUserConfig(__DEFAULT_USER__)

    if result["status"] == "success":
        await ctx.reply(f"Configuration Options (defaults):\n```\n{result['msg']}\n```")
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
        # print(f"user_configuration: {uc}")

        await ctx.reply(
            f"{ctx.author.name}'s config:\n```{json.dumps(Configuration(u).settings,sort_keys=True,indent=4)}```"
        )

    else:
        split = shlex.split(arg)
        # print(f"Split: {split}")

        if len(split) == 1:
            await ctx.reply(
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


# New Functionality Below


@bot.command(name="parrot")
async def _parrot(ctx):

    # Send Intiial Reply
    m = await ctx.reply(PARROT_EMOJI)

    # Get Username
    u = str(ctx.author.id)

    # Get User State with init_new for regsitration.
    s = bot.states.get(u)
    if s is None:
        bot.states[u] = State(u, bot)
        s = bot.states[u]
        logger.debug(f"Registering {u}")

    # Create New Object, then Link to The tracked message.
    new_parrot = ParrotMessage(
        channel_id=m.channel.id, message_id=m.id, word=PARROT_EMOJI
    )

    identifier = message_identifier(
        channel_id=ctx.channel.id, message_id=ctx.message.id
    )

    logger.debug(
        "New Parrot: \n" + json.dumps(dict(new_parrot), sort_keys=True, indent=4)
    )

    s.state[identifier] = new_parrot


@bot.command(name="state", rest_is_raw=True)
async def _state(ctx, *, args: str):

    # Get Username
    u = str(ctx.author.id)

    # Get User State with init_new for regsitration.
    s = bot.states.get(u)
    if s is None:
        bot.states[u] = State(u, bot)
        s = bot.states[u]
        logger.debug(f"Registering {u}")

    if not args:
        # Empty args we show user state.

        delimiters_state = {
            "start": f"**State for {ctx.author.name}**\n" + r"```",
            "end": r"```",
        }

        delimiters_pins = {
            "start": f"**Pins for {ctx.author.name}**\n" + r"```",
            "end": r"```",
        }

        # await ctx.reply(
        #     delimiters_state["start"]
        #     + json.dumps(s.state, sort_keys=True, indent=4)
        #     + delimiters_state["end"]
        # )

        # await ctx.reply(
        #     delimiters_pins["start"]
        #     + json.dumps(s.pins, sort_keys=True, indent=4)
        #     + delimiters_pins["end"]
        # )
        print(str(s))

    else:

        split = shlex.split(args)
        if split[0] == "clear":
            s.state = dict()
            await ctx.message.add_reaction(CHECKMARK_EMOJI)
        else:

            # Return the length of instances.

            x = await s.fetch_tracker(type=split[0])
            await ctx.reply(f"User {u} has {len(x)} {split[0]} instances.")
            logger.debug(f"User {u} has {len(x)} {split[0]} instances: {x}.")
        pass


@bot.command(name="pins", rest_is_raw=True)
async def _get_pins_v2(ctx, *, args: str):
    u = str(ctx.author.id)

    # Get State
    s = bot.states.get(u)
    if s is None:
        bot.states[u] = State(u, bot)
        s = bot.states[u]

    split = shlex.split(args)
    action = split[0] if len(split) > 0 else ""
    if action in {"", "reverse", "here"}:
        if not action:
            reverse = False
            condition = lambda a: True
        elif action == "reverse":
            reverse = True
            condition = lambda a: True
        elif action == "here":
            reverse = False
            condition = lambda a: str(a.channel_id) == str(ctx.channel.id)

        # Use context to reply to user. Then fetch partial identifier.
        # This will be used to construct ShowPinsPanel.
        # Build pages first, then construct ShowPinsPanel
        # Append ShowPinsPanel to user state to be aware of interactions.

        m = await ctx.reply("Fetching Pins...")

        message_id = m.id
        channel_id = m.channel.id

        identifier = message_identifier(channel_id=channel_id, message_id=message_id)

        logger.debug(f"List of Pins: {list(s.pins.values())}")

        # Build pages from List of Pins.
        pages = ShowPinsPanel.build_pages(
            pins=list(s.pins.values()),
            author_name=ctx.author.name,
            oldest_first=reverse,
            condition=condition,
        )

        # Construct the Panel Reply
        x = ShowPinsPanel(
            channel_id=channel_id, message_id=message_id, pages=pages, current_page=0
        )

        await x.on_reaction_add(emoji=PAGE_EMOJIS["next_page"], bot=bot)
        s.state[identifier] = x

    elif action == "clear":
        s.pins = dict()
        await ctx.message.add_reaction(CHECKMARK_EMOJI)


# @bot.event
# async def on_command_error(ctx, error):
#     z = f'Command Error: `{error}`'

#     await ctx.send(f'{z}')
#     logger.warning(f'{z}, {error.args} {type(error)}')


@bot.event
async def on_raw_reaction_add(payload):

    channel_id = payload.channel_id
    message_id = payload.message_id
    user = str(payload.user_id)
    emoji = payload.emoji.name
    display_name = bot.get_user(int(user)).name

    if user != str(bot.user.id):

        s = bot.states.get(user)
        if s is None:
            bot.states[user] = State(user, bot)
            s = bot.states[user]
        identifier = message_identifier(channel_id=channel_id, message_id=message_id)

        if emoji == STAR_EMOJI:
            """
            Add Pin
            """
            logger.debug(f"{STAR_EMOJI} add from {display_name}")

            z = StarredMessage(
                channel_id=channel_id,
                message_id=message_id,
            )

            await z.refresh(bot)
            await react_to_message(
                bot=bot,
                channel_id=channel_id,
                message_id=message_id,
                emoji=STAR_EMOJI,
                action="add",
            )

            # Attach to user's State
            # Now add a Pinsv3 to track the emoji removal.

            w = PinPanel(
                channel_id=channel_id,
                message_id=message_id,
                user=user,
            )

            s.pins[identifier] = z
            s.state[identifier] = w

            # logger.debug(f's.pins: {s.pins}')
            # logger.debug(f's.state: {s.state}')

        else:

            # Now handle the interaction for any generic tracked object
            z = s.state.get(identifier)
            if z is not None:
                await z.on_reaction_add(emoji, bot)


@bot.event
async def on_raw_reaction_remove(payload):

    channel_id = payload.channel_id
    message_id = payload.message_id
    user = str(payload.user_id)
    emoji = payload.emoji.name
    display_name = bot.get_user(int(user)).name

    if user != str(bot.user.id):

        s = bot.states.get(user)
        if s is None:
            bot.states[user] = State(user, bot)
            s = bot.states[user]

        identifier = message_identifier(channel_id=channel_id, message_id=message_id)

        if emoji == STAR_EMOJI:

            """
            Removes the pin if the pin exists.
            """
            logger.debug(f"{STAR_EMOJI} removal from {display_name}")

            try:
                z = s.state.pop(identifier)
            except KeyError:
                pass

            try:
                z = s.pins.pop(identifier)
            except KeyError:
                pass

            # Now find the message and unreact.
            await react_to_message(
                bot=bot,
                channel_id=channel_id,
                message_id=message_id,
                emoji=STAR_EMOJI,
                action="remove",
            )
        else:

            z = s.state.get(identifier)
            if z is not None:
                await z.on_reaction_remove(emoji, bot)


@bot.event
async def on_raw_message_edit(payload):

    channel_id = payload.channel_id
    message_id = payload.message_id

    # get user of the edit.
    # no choice but to fetch partial
    channel = bot.get_channel(channel_id)
    if not channel:
        channel = await bot.fetch_channel(channel_id)

    partial = discord.PartialMessage(channel=channel, id=int(message_id))

    full = await partial.fetch()
    u = str(full.author.id)

    if u != bot.user.id:

        s = bot.states.get(u)
        if s is None:
            bot.states[u] = State(u, bot)
            s = bot.states[u]
            logger.debug(f"Registering {u}")

        identifier = message_identifier(channel_id=channel_id, message_id=message_id)

        z = s.state.get(identifier)

        if z is not None:

            await z.on_edit(after=full.content, bot=bot)  # this might be empty.


@bot.event
async def on_command(ctx):
    fulluser = f"{ctx.author} -> {ctx.author.id}"

    logger.info(f'{ctx.author} invoked "{ctx.command}" w/ args {ctx.args[1:]}.')
    # logger.debug(f"{fulluser}")


@bot.event
async def on_command_completion(ctx):
    """
    Increments the user's config.usage and config.last_used.
    """
    userid = str(ctx.author.id)
    Configuration.incrementUserConfig(str(userid))






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
