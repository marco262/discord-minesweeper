from json import loads

import discord
from discord.ext.commands import Bot

from src.list_bot.list_functions import load_list_functions
from src.minesweeper.minesweeper import new_game

VERSION = (0, 0, 1)

with open("conf/credentials.json") as f:
    json = loads(f.read())
    TOKEN = json["token"]
    MASTER_ID = json["master_id"]


def init_bot():
    return Bot(command_prefix="~")


def load_functions(bot):
    load_list_functions(bot)

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
        if len(output) > 2000:
            await context.send("Oops! That map is too long to send. ({} > 2000). ".format(len(output)) +
                               "Try reducing the map size or adding more bombs.")
        if send_to_channel:
            await context.send(output)
        else:
            await context.author.send(output)

    @bot.command(name='logout')
    async def logout(context):
        if context.author.id == MASTER_ID:
            print("Logging out...")
            await bot.change_presence(status=discord.Status.offline)
            await bot.logout()


def run_bot():
    bot = init_bot()
    load_functions(bot)
    bot.run(TOKEN)
