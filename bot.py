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
        await channel.send("Will wait for %d minutes" % minutes)
        await asyncio.sleep(minutes * 60)
        await channel.send("Time’s up!")
    # await channel.send(message.content)

client.run(token)

