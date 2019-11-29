import traceback
from time import ctime

from discord import Message
from discord.ext.commands import Context, Cog, command

from src.list_bot import list_functions


class ListCommands(Cog):
    
    def __init__(self, bot):
        self.bot = bot
        list_functions.check_version()

    @staticmethod
    async def handle_command(context, func) -> Message:
        cmd = context.prefix + context.command.name
        # Get everything after the command
        message = context.message.content[len(cmd):].strip()
        try:
            output, edit, message_id = func(context, context.author, message)
            if message_id:
                retrieved_message = await context.fetch_message(message_id)
                await retrieved_message.edit(content=edit)
            if output:
                return await context.send(output)
        except Exception as e:
            print(ctime())
            traceback.print_exc()
            await context.send(e.args[0])
            print()

    @command(name='newlist', help="Create a new list")
    async def new_list(self, context: Context):
        response_message = await self.handle_command(context, list_functions.new_list)
        if response_message:
            list_functions.set_last_message_id(context, context.author, response_message)

    @command(name='list', help="Display your current list")
    async def show_list(self, context: Context):
        response_message = await self.handle_command(context, list_functions.show_list)
        if response_message:
            list_functions.set_last_message_id(context, context.author, response_message)

    @command(name='add', help="Add items to your list")
    async def add(self, context: Context):
        await self.handle_command(context, list_functions.add_tasks)

    @command(name='remove', help="Remove items from your list")
    async def remove(self, context: Context):
        await self.handle_command(context, list_functions.remove_tasks)

    @command(name='top', help="Bump a task to the top of your list")
    async def top(self, context: Context):
        await self.handle_command(context, list_functions.top)

    @command(name='bottom', help="Bump a task to the bottom of your list")
    async def bottom(self, context: Context):
        await self.handle_command(context, list_functions.bottom)

    @command(name='move', help="Move a task to a new place in your list")
    async def move(self, context: Context):
        await self.handle_command(context, list_functions.move)

    @command(name='start', help="Start a task")
    async def start(self, context: Context):
        await self.handle_command(context, list_functions.start_task)

    @command(name='stop', help="Stop a task")
    async def stop(self, context: Context):
        await self.handle_command(context, list_functions.stop_task)

    @command(name='check', help="Check a task")
    async def check(self, context: Context):
        await self.handle_command(context, list_functions.check_task)

    @command(name='checklist', help="Check a list of task numbers")
    async def checklist(self, context: Context):
        await self.handle_command(context, list_functions.check_list)

    @command(name='checkall', help="Check all remaining tasks on your list")
    async def checkall(self, context: Context):
        await self.handle_command(context, list_functions.check_all)

    @command(name='uncheck', help="Uncheck a task")
    async def uncheck(self, context: Context):
        await self.handle_command(context, list_functions.uncheck_task)

    @command(name='tasktime', help="Display the times spent on all tasks")
    async def task_time(self, context: Context):
        await self.handle_command(context, list_functions.task_time)

    @command(name='clear', help="Clear all checked tasks")
    async def clear(self, context: Context):
        await self.handle_command(context, list_functions.clear_checked_tasks)
