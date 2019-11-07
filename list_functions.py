from discord.ext.commands import Bot

from db import Db


def load_list_functions(bot: Bot):

    @bot.command(name='create_tables')
    async def create_tables(context):
        with Db() as db:
            db.list_tables()

