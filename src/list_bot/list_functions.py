from discord.ext.commands import Bot, Context

from src.list_bot import list_engine
from src.utils import ListBotError


async def handle_list_function(context, func):
    command = context.prefix + context.command.name
    # Get everything after the command
    message = context.message.content[len(command):].strip()
    try:
        output = func(context, context.author.id, context.author.name, message)
    except Exception as e:
        output = e.args
    await context.send(output)


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
    async def top(context: Context):
        await handle_list_function(context, list_engine.top)

    @bot.command(name='bottom')
    async def bottom(context: Context):
        await handle_list_function(context, list_engine.bottom)

    @bot.command(name='move')
    async def move(context: Context):
        await handle_list_function(context, list_engine.move)

    @bot.command(name='start')
    async def start(context: Context):
        await handle_list_function(context, list_engine.start_task)

    @bot.command(name='stop')
    async def stop(context: Context):
        await handle_list_function(context, list_engine.stop_task)

    @bot.command(name='check')
    async def check(context: Context):
        await handle_list_function(context, list_engine.check_task)

    @bot.command(name='uncheck')
    async def uncheck(context: Context):
        await handle_list_function(context, list_engine.uncheck_task)
