import toml
from discord.ext.commands import Bot, Context, Cog, command, Command

from src.list_bot import list_engine


class ListFunctions(Cog):
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.init_help()
        self.load_commands()

    def init_help(self):
        """
        Loads command information from help.toml. Includes function names to use in list_engine (if different
        than command name) and the help text.
        :return:
        """
        with open("src/list_bot/help.toml") as f:
            self.help = toml.loads(f.read())
        for name, options in self.help.items():
            if "func_name" not in options:
                options["func_name"] = name
            options["help"] = options["help"].strip()

    def load_commands(self):
        """
        Dynamically create all the commands, using the command info in the help file. Each command makes use of
        handle_list_function to simplify things.
        :return:
        """
        for name, options in self.help.items():
            async def func(context):
                await self.handle_list_function(context, getattr(list_engine, options["func_name"]))
            c = Command(func, name=name, help=options["help"])
            # Make this command a part of this Cog class
            c.cog = self
            self.bot.add_command(c)

    @staticmethod
    async def handle_list_function(context, func):
        cmd = context.prefix + context.command.name
        # Get everything after the command
        message = context.message.content[len(cmd):].strip()
        try:
            output = func(context, context.author.id, context.author.name, message)
        except Exception as e:
            output = e.args
        await context.send(output)

    @command(name='add', help="Add items to your list")
    async def add(self, context: Context):
        await self.handle_list_function(context, list_engine.add)

    @command(name='remove', help="Remove items from your list")
    async def remove(self, context: Context):
        await self.handle_list_function(context, list_engine.remove)

    @command(name='top', help="Bump a task to the top of your list")
    async def top(self, context: Context):
        await self.handle_list_function(context, list_engine.top)

    @command(name='bottom', help="Bump a task to the bottom of your list")
    async def bottom(self, context: Context):
        await self.handle_list_function(context, list_engine.bottom)

    @command(name='move', help="Move a task to a new place in your list")
    async def move(self, context: Context):
        await self.handle_list_function(context, list_engine.move)

    @command(name='start', help="Start a task")
    async def start(self, context: Context):
        await self.handle_list_function(context, list_engine.start)

    @command(name='stop', help="Stop a task")
    async def stop(self, context: Context):
        await self.handle_list_function(context, list_engine.stop)

    @command(name='check', help="Check a task")
    async def check(self, context: Context):
        await self.handle_list_function(context, list_engine.check)

    @command(name='uncheck', help="Uncheck a task")
    async def uncheck(self, context: Context):
        await self.handle_list_function(context, list_engine.uncheck)

    @command(name='tasktime', help="Display the times spent on all tasks")
    async def task_time(self, context: Context):
        await self.handle_list_function(context, list_engine.tasktime)

    @command(name='clear', help="Clear all checked tasks")
    async def clear(self, context: Context):
        await self.handle_list_function(context, list_engine.clear)
