from discord.ext.commands import Bot

from src.list_bot import list_engine


async def handle_list_function(context, func):
    await context.send(func(context))


def load_list_functions(bot: Bot):

    @bot.command(name='newlist')
    def new_list(context):
        handle_list_function(context, list_engine.new_list)

    @bot.command(name='list')
    def show_list(context):
        handle_list_function(context, list_engine.show_list)



