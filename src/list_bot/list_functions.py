from re import match

from discord import Message
from discord.ext.commands import Context

from src.db.db import Db
from src.utils import print_task_list, find_task_id_in_list, pretty_task_time, get_list_items, get_display_mode


def new_list(context, owner: Message.author, message):
    if message == "":
        return "I need items to make a list. Put each separate item on a new line."
    task_names = message.split("\n")
    with Db() as db:
        db.add_owner(owner.id, owner.name)
        task_ids = db.add_tasks(task_names, owner.id)
        db.new_list(task_ids, owner.id)
        return f"Created a new list for {owner.name}\n" + print_task_list(db, owner), None, None


def show_list(context, owner: Message.author, message):
    with Db() as db:
        return f"{owner.name}'s list\n" + print_task_list(db, owner), None, None


def add_tasks(context, owner: Message.author, message):
    with Db() as db:
        task_list = get_list_items(db, owner)
        new_row_ids = db.add_tasks(message.split("\n"), owner.id)
        db.update_list_items(task_list + new_row_ids, owner.id)
        return get_display_mode(context, db, owner, f"{owner.name} added tasks to their list")


def remove_tasks(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        for item in message.split("\n"):
            task_id = find_task_id_in_list(db, task_ids, item)
            task_ids.remove(task_id)
        db.update_list_items(task_ids, owner.id)
        return get_display_mode(context, db, owner, f"{owner.name} removed tasks from their list")


def top(context, owner: Message.author, message):
    return _reorder_task(context, owner, message, 1)


def bottom(context, owner: Message.author, message):
    return _reorder_task(context, owner, message, -1)


def move(context, owner: Message.author, message):
    m = match(r'^(.*) (\d+)$', message)
    if not m:
        return "Sorry, I don't understand. Accepted format: ~move <item> <position>"
    return _reorder_task(context, owner, m.group(1).strip('"'), int(m.group(2)))


def _reorder_task(context, owner: Message.author, item: str, position: int):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        task_id = find_task_id_in_list(db, task_ids, item)
        task_ids.remove(task_id)
        if position == -1:
            task_ids.append(task_id)
        else:
            task_ids.insert(position - 1, task_id)
        db.update_list_items(task_ids, owner.id)
        return get_display_mode(context, db, owner, f"{owner.name} moved task '{item}' to {position}")


def start_task(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) == "STARTED":
            return "That task is already started.", None, None
        if "STARTED" in db.get_task_states(task_ids):
            return "You can only have one started task at a time.", None, None
        db.start_task(task_id)
        return get_display_mode(context, db, owner, f"{owner.name} started task '{message}'")


def stop_task(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "STARTED":
            return "That task hasn't been started.", None, None
        db.stop_task(task_id)
        return get_display_mode(context, db, owner, f"{owner.name} stopped task '{message}'")


def check_task(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) == "CHECKED":
            return "That task hasn't been started.", None, None
        db.complete_task(task_id)
        return get_display_mode(context, db, owner, f"{owner.name} finished task '{message}'")


def check_list(context, owner: Message.author, message):
    with Db() as db:
        list_items = get_list_items(db, owner)
        tasks = message.split(" ")
        if not all([s.isdigit() for s in tasks]):
            return "All arguments must be positions of tasks, not names.", None, None
        task_ids = []
        for task in tasks:
            task_id = find_task_id_in_list(db, list_items, task)
            if db.get_task_state(task_id) == "CHECKED":
                return f"Task {task} has already been finished.", None, None
            task_ids.append(task_id)
        for task_id in task_ids:
            db.complete_task(task_id)
        return get_display_mode(context, db, owner, f"{owner.name} finished tasks '{message}'")


def check_all(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        for task_id in task_ids:
            if db.get_task_state(task_id) != "CHECKED":
                db.complete_task(task_id)
        return get_display_mode(context, db, owner, f"{owner.name} finished all tasks in their list.")


def uncheck_task(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "CHECKED":
            return "That task hasn't been completed.", None, None
        db.uncomplete_task(task_id)
        return get_display_mode(context, db, owner, f"{owner.name} unchecked task '{message}'")


def task_time(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        tasks = db.get_tasks(task_ids)
        output = f"{owner.name} times\n"
        for t in tasks:
            output += f"{t['name']}: {pretty_task_time(t['time_spent_sec'])}\n"
        output += f"\nTotal time: {pretty_task_time(sum([t['time_spent_sec'] for t in tasks]))}"
    return output, None, None


def clear_checked_tasks(context, owner: Message.author, message):
    with Db() as db:
        task_ids = get_list_items(db, owner)
        task_states = db.get_task_states(task_ids)
        tasks = zip(task_ids, task_states)
        unchecked_tasks = []
        for task_id, state in tasks:
            if state != "CHECKED":
                unchecked_tasks.append(task_id)
        db.update_list_items(unchecked_tasks, owner.id)
        return f"{owner.name}'s list\n" + print_task_list(db, owner), None, None


def set_last_message_id(context: Context, owner: Message.author, response_message: Message):
    with Db() as db:
        db.set_last_message_id(owner.id, context.channel.id, response_message.id)
