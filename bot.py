import asyncio
import discord

token = open(".token").read()

client = discord.Client()

open_rounds = {} # dict from (guild_name, channel_name) to (user_mention, moves) or None

async def play_audio(voice_channel, audio_source):
    future = asyncio.get_event_loop().create_future()
    def after_play(error):
        if error:
            future.set_exception(error)
        else:
            future.set_result(None)
    audio = await discord.FFmpegOpusAudio.from_probe(audio_source)
    connection = await voice_channel.connect()
    connection.play(audio, after=after_play)
    await future
    await connection.disconnect()

async def start_countdown(channel, minutes):
    countdown = await channel.send("Time left: %d minutes" % minutes)
    edit = asyncio.sleep(0)
    while minutes > 0:
        sleep = asyncio.sleep(60)
        await asyncio.gather(sleep, edit)
        minutes -= 1
        edit = countdown.edit(content="Time left: %d minutes" % minutes)
    await edit
    await countdown.edit(content="Time’s up!")
    await channel.send("Time’s up!")

async def countdown_seconds(channel, seconds):
    countdown = await channel.send("Time left: %d seconds" % seconds)
    edit = asyncio.sleep(0)
    while seconds > 0:
        sleep = asyncio.sleep(1)
        await asyncio.gather(sleep, edit)
        seconds -= 1
        edit = countdown.edit(content="Time left: %d seconds" % seconds)
    await edit
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
        voice_channel = message.author.voice and message.author.voice.channel
        await start_countdown(channel, minutes)
        if voice_channel:
            await play_audio(voice_channel, "countdown-stop.mp3")
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
            await countdown_seconds(channel, seconds=60)
            best_user_mention, best_moves = open_rounds[round_marker]
            await channel.send("%s, show us your %d moves!" % (best_user_mention, best_moves))
            del open_rounds[round_marker]
        else:
            previous_user_mention, previous_moves = open_round
            if moves < previous_moves:
                open_rounds[round_marker] = (message.author.mention, moves)
    # await channel.send(message.content)

client.run(token)

