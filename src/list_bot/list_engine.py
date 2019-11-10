from re import match

from src.db.db import Db
from src.utils import print_task_list, find_task_id_in_list


def new_list(context, owner_id, owner_name, message):
    task_names = message.split("\n")

    with Db() as db:
        db.add_owner(owner_id, owner_name)
        task_ids = db.add_tasks(task_names, owner_id)
        db.new_list(task_ids, owner_id)
        task_list = db.get_tasks(task_ids)

    return f"Created a new list for {owner_name}\n" + print_task_list(task_list)


def show_list(context, owner_id, owner_name, message):
    with Db() as db:
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def add_tasks(context, owner_id, owner_name, message):
    with Db() as db:
        new_row_ids = db.add_tasks(message.split("\n"), owner_id)
        task_list = db.get_list_items(owner_id)
        db.update_list_items(task_list + new_row_ids, owner_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def remove_tasks(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = db.get_list_items(owner_id)
        for item in message.split("\n"):
            task_id = find_task_id_in_list(db, task_ids, item)
            task_ids.remove(task_id)
        db.update_list_items(task_ids, owner_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def top(context, owner_id, owner_name, message):
    return _reorder_task(owner_id, owner_name, message, 1)


def bottom(context, owner_id, owner_name, message):
    return _reorder_task(owner_id, owner_name, message, -1)


def move(context, owner_id, owner_name, message):
    m = match(r'"(.*?)" (\d+)', message)
    if not m:
        return "Sorry, I don't understand. Accepted format: ~move \"<item>\" <position>"
    return _reorder_task(owner_id, owner_name, m.group(1), int(m.group(2)))


def _reorder_task(owner_id: int, owner_name: str, item: str, position: int):
    with Db() as db:
        task_ids = db.get_list_items(owner_id)
        task_id = find_task_id_in_list(db, task_ids, item)
        task_ids.remove(task_id)
        if position == -1:
            task_ids.append(task_id)
        else:
            task_ids.insert(position - 1, task_id)
        db.update_list_items(task_ids, owner_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def start_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = db.get_list_items(owner_id)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) == "STARTED":
            return "That task is already started."
        db.start_task(task_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def stop_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = db.get_list_items(owner_id)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "STARTED":
            return "That task hasn't been started."
        db.stop_task(task_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def check_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = db.get_list_items(owner_id)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "STARTED":
            return "That task hasn't been started."
        db.complete_task(task_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)


def uncheck_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = db.get_list_items(owner_id)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "CHECKED":
            return "That task hasn't been completed."
        db.uncomplete_task(task_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)
