from json import loads

import discord
from discord.ext.commands import Bot

from minesweeper import new_game

VERSION = (0, 0, 1)

with open("credentials.json") as f:
    json = loads(f.read())
    TOKEN = json["token"]
    GUILD = json["guild"]

bot = Bot(command_prefix="~")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("~help"))
    print(f"{bot.user.name} has connected to Discord!")


@bot.command(name='version')
async def version(context):
    await context.send("Version " + ".".join([str(c) for c in VERSION]))


@bot.command(name='game', help="[width] [height] [# of bombs] [public]")
async def game(context, width: int=None, height: int=None, bombs: int=10, public: str=""):
    send_to_channel = (public == "public")
    output = new_game(width, height, bombs)
    if send_to_channel:
        await context.send(output)
    else:
        await context.author.send(output)


if __name__ == "__main__":
    bot.run(TOKEN)
