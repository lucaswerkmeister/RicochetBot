import asyncio
import discord

token = open(".token").read()

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name="Auregann's salon")
    channel = discord.utils.get(guild.channels, name='tests')
    # await channel.send("Hello, World!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    channel = message.channel
    if channel.name != "tests":
        return
    if message.content.startswith("-timer "):
        arg = message.content[len("-timer "):]
        try:
            minutes = int(arg)
        except ValueError:
            await channel.send("Invalid duration (in minutes)!")
            return
        countdown = await channel.send(content="Time left: %d minutes" % minutes)
        while minutes > 0:
            await asyncio.sleep(60) # TODO timer skew from also awaiting countdown.edit() below
            minutes -= 1
            await countdown.edit(content="Time left: %d minutes" % minutes)
        await countdown.edit(content="Time’s up!")
    # await channel.send(message.content)

client.run(token)

