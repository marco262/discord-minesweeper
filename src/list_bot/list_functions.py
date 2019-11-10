from discord.ext.commands import Bot, Context

from src.list_bot import list_engine


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

    @bot.command(name='newlist', category="List", help="Create a new list")
    async def new_list(context: Context):
        await handle_list_function(context, list_engine.new_list)

    @bot.command(name='list', category="List", help="Display your current list")
    async def show_list(context: Context):
        await handle_list_function(context, list_engine.show_list)

    @bot.command(name='add', category="List", help="Add items to your list")
    async def add(context: Context):
        await handle_list_function(context, list_engine.add_tasks)

    @bot.command(name='remove', category="List", help="Remove items from your list")
    async def add(context: Context):
        await handle_list_function(context, list_engine.remove_tasks)

    @bot.command(name='top', category="List", help="Bump a task to the top of your list")
    async def top(context: Context):
        await handle_list_function(context, list_engine.top)

    @bot.command(name='bottom', category="List", help="Bump a task to the bottom of your list")
    async def bottom(context: Context):
        await handle_list_function(context, list_engine.bottom)

    @bot.command(name='move', category="List", help="Move a task to a new place in your list")
    async def move(context: Context):
        await handle_list_function(context, list_engine.move)

    @bot.command(name='start', category="List", help="Start a task")
    async def start(context: Context):
        await handle_list_function(context, list_engine.start_task)

    @bot.command(name='stop', category="List", help="Stop a task")
    async def stop(context: Context):
        await handle_list_function(context, list_engine.stop_task)

    @bot.command(name='check', category="List", help="Check a task")
    async def check(context: Context):
        await handle_list_function(context, list_engine.check_task)

    @bot.command(name='uncheck', category="List", help="Uncheck a task")
    async def uncheck(context: Context):
        await handle_list_function(context, list_engine.uncheck_task)

    @bot.command(name='tasktime', category="List", help="Display the times spent on all tasks")
    async def task_time(context: Context):
        await handle_list_function(context, list_engine.task_time)

    @bot.command(name='clear', category="List", help="Clear all checked tasks")
    async def clear(context: Context):
        await handle_list_function(context, list_engine.clear_checked_tasks)
