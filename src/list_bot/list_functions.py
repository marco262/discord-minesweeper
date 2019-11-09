from discord.ext.commands import Bot

from src.db.db import Db
from src.utils import print_task_list


def load_list_functions(bot: Bot):

    @bot.command(name='newlist')
    async def new_list(context):
        owner_name = context.author.name
        owner_id = context.author.id
        args_list = context.message.content.split("\n")
        # If message was on a single line, use whatever is after the command
        if len(args_list) == 1:
            task_names = [args_list[0].split(" ", 1)[1]]
        else:
            task_names = args_list[1:]

        with Db() as db:
            db.add_owner(owner_id, owner_name)
            task_ids = db.add_tasks(task_names, owner_id)
            db.new_list(task_ids, owner_id)
            task_list = db.get_tasks(task_ids)

        output = f"Created a new list for {owner_name}\n" + print_task_list(task_list)
        await context.send(output)

    @bot.command(name='list')
    async def show_list(context):
        owner_name = context.author.name
        owner_id = context.author.id
        with Db() as db:
            task_list = db.get_tasks(db.get_list_items(owner_id))

        output = f"{owner_name}'s list\n" + print_task_list(task_list)
        await context.send(output)


