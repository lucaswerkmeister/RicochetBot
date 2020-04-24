import asyncio
import discord

token = open(".token").read()

client = discord.Client()

open_rounds = {} # dict from (guild_name, channel_name) to (user_mention, moves) or None

async def start_countdown(channel, minutes):
    countdown = await channel.send("Time left: %d minutes" % minutes)
    while minutes > 0:
        await asyncio.sleep(60) # TODO timer skew from also awaiting countdown.edit() below
        minutes -= 1
        await countdown.edit(content="Time left: %d minutes" % minutes)
    await countdown.edit(content="Time’s up!")
    await channel.send("Time’s up!")

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name="Auregann's salon")
    channel = discord.utils.get(guild.channels, name='tests')
    # await channel.send("Hello, World!")

@client.event
async def on_message(message):
    global open_rounds
    guild = message.guild
    channel = message.channel
    round_marker = (guild.name, channel.name)
    if message.author == client.user:
        return
    if channel.name != "tests":
        return
    if message.content.startswith("-timer "):
        arg = message.content[len("-timer "):]
        try:
            minutes = int(arg)
        except ValueError:
            await channel.send("Invalid duration (in minutes)!")
            return
        await start_countdown(channel, minutes)
    if message.content == "-round":
        await channel.send("@ here New round!")
        open_rounds[round_marker] = None
    if message.content.isnumeric() and message.content.isascii():
        if round_marker not in open_rounds:
            return
        moves = int(message.content)
        open_round = open_rounds[round_marker]
        if open_round is None:
            open_rounds[round_marker] = (message.author.mention, moves)
            await start_countdown(channel, minutes=1)
            best_user_mention, best_moves = open_rounds[round_marker]
            await channel.send("%s, show us your %d moves!" % (best_user_mention, best_moves))
            del open_rounds[round_marker]
        else:
            previous_user_mention, previous_moves = open_round
            if moves < previous_moves:
                open_rounds[round_marker] = (message.author.mention, moves)
    # await channel.send(message.content)

client.run(token)

