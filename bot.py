import discord

token = open(".token").read()

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name="Auregann's salon")
    channel = discord.utils.get(guild.channels, name='tests')
    await channel.send("Hello, World!")
    print(dir(channel))

client.run(token)

