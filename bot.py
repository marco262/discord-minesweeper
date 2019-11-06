from json import loads

import discord
from discord.ext.commands import Bot

from emoji_parser import grid_to_emoji
from minesweeper import build_game

VERSION = (0, 0, 1)

with open("credentials.json") as f:
    json = loads(f.read())
    TOKEN = json["token"]
    GUILD = json["guild"]

bot = Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.command(name='version')
async def version(context):
    await context.send("Version " + ".".join([str(c) for c in VERSION]))


@bot.command(name='game')
async def game(context):
    grid = build_game()
    await context.send(grid_to_emoji(grid))


if __name__ == "__main__":
    bot.run(TOKEN)
