from discord.ext.commands import Bot, Context

from src.list_bot import list_engine


async def handle_list_function(context, func):
    command = context.prefix + context.command.name
    # Get everything after the command
    message = context.message.content[len(command):].strip()
    await context.send(func(
        context,
        context.author.id,
        context.author.name,
        message
    ))


def load_list_functions(bot: Bot):

    @bot.command(name='newlist')
    async def new_list(context: Context):
        await handle_list_function(context, list_engine.new_list)

    @bot.command(name='list')
    async def show_list(context: Context):
        await handle_list_function(context, list_engine.show_list)

    @bot.command(name='add')
    async def add(context: Context):
        await handle_list_function(context, list_engine.add_tasks)

    @bot.command(name='remove')
    async def add(context: Context):
        await handle_list_function(context, list_engine.remove_tasks)

    @bot.command(name='top')
    async def add(context: Context):
        await handle_list_function(context, list_engine.top)

    @bot.command(name='bottom')
    async def add(context: Context):
        await handle_list_function(context, list_engine.bottom)

    @bot.command(name='move')
    async def add(context: Context):
        await handle_list_function(context, list_engine.move)
