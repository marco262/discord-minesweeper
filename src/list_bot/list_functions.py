import toml
from discord.ext.commands import Bot, Context, Cog, command, Command

from src.list_bot import list_engine


class ListFunctions(Cog):
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.help = self.init_help()
        self.load_commands()

    def init_help(self):
        """
        Loads command information from help.toml. Includes function names to use in list_engine (if different
        than command name) and the help text.
        :return:
        """
        with open("src/list_bot/help.toml") as f:
            help_data = toml.loads(f.read())
        for name, options in help_data.items():
            if "func_name" not in options:
                options["func_name"] = name
            options["help"] = options["help"].strip()
        return help_data

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
