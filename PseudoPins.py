import discord

# PseudoPins

#Addressing:
#Guild.Channel.Message
def channel_identifier(ctx):

    if isinstance(ctx.channel,discord.DMChannel):
        name = f'dm_{ctx.channel.recipient}'
        id = ctx.channel.id
        result = {
            'name': f'dm_{ctx.channel.recipient.id}',
            'title': f'dm_{ctx.channel.recipient.name}',
            'id': str(ctx.channel.recipient.id),
            
            'type': 'dm'
        }
    elif isinstance(ctx.channel, (discord.TextChannel,
    discord.GroupChannel, discord.WelcomeChannel)):
        result = {\
            'name': f'channel_{ctx.channel.id}',
            'title': f'channel_{ctx.channel.name}',

            'id': str(ctx.channel.id),
            'guild_id': str(ctx.guild.id),
            'guild_title': str(ctx.guild.name),

            'type': 'channel',
        }
    elif isinstance(ctx.channel, discord.Thread):
        result={\
            'name': f'thread_{ctx.channel.id}',
            'title': f'channel_{ctx.channel.name}',
            
            'id': ctx.channel.id,
            'guild_id': str(ctx.guild.id),
            'guild_title': str(ctx.guild.name),

            'parent_channel': ctx.channel.parent.id,
            'type': 'thread',
        }
    if ctx.message.reference:
        # print(f'Reference Detected: {ctx.message.reference}')

        result['reference']={\
        'referenced_id': ctx.message.reference.message_id,
        'referenced_message': ctx.message.reference.cached_message,
        }
    return result

class Pin:

    pass
