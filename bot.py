import asyncio
import discord

token = open(".token").read()

client = discord.Client()

open_rounds = {} # dict from (guild_name, channel_name) to ([voice_channel], [user_mention, moves])

async def play_audio(voice_channel, audio_source):
    """Join voice_channel, play audio_source, disconnect again."""
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

async def countdown_minutes(channel, minutes):
    """Send a countdown message (updated each minute)
    and another one when the countdown finishes."""
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
    """Send a countdown message (updated each second)
    and another one when the countdown finishes."""
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

def user_voice_channel(user):
    return user.voice and user.voice.channel

@client.event
async def on_message(message):
    """React to a message. Main bot logic."""
    global open_rounds
    guild = message.guild
    channel = message.channel
    round_marker = (guild.name, channel.name)
    if message.author == client.user:
        return
    if message.content.startswith("-timer "):
        arg = message.content[len("-timer "):]
        try:
            minutes = int(arg)
        except ValueError:
            await channel.send("Invalid duration (in minutes)!")
            return
        voice_channel = user_voice_channel(message.author)
        await countdown_minutes(channel, minutes)
        if voice_channel:
            await play_audio(voice_channel, "countdown-stop.mp3")
    if message.content == "-round":
        await channel.send("%s New round!" % ("@ here" if channel.name == "tests" else "@here"))
        open_rounds[round_marker] = (user_voice_channel(message.author), None, None)
    if message.content.isnumeric() and message.content.isascii():
        if round_marker not in open_rounds:
            return
        moves = int(message.content)
        voice_channel, previous_user_mention, previous_moves = open_rounds[round_marker]
        if previous_moves is None:
            open_rounds[round_marker] = (voice_channel, message.author.mention, moves)
            await asyncio.gather(
                countdown_seconds(channel, seconds=60),
                play_audio(voice_channel, "countdown-start.mp3") if voice_channel else asyncio.sleep(0),
            )
            voice_channel, best_user_mention, best_moves = open_rounds[round_marker]
            await asyncio.gather(
                channel.send("%s, show us your %d moves!" % (best_user_mention, best_moves)),
                play_audio(voice_channel, "countdown-stop.mp3") if voice_channel else asyncio.sleep(0),
            )
            del open_rounds[round_marker]
        else:
            if moves < previous_moves:
                open_rounds[round_marker] = (voice_channel, message.author.mention, moves)

client.run(token)

