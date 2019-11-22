from re import match

from src.db.db import Db
from src.utils import print_task_list, find_task_id_in_list, pretty_task_time, get_list_items


def new_list(context, owner_id, owner_name, message):
    if message == "":
        return "I need items to make a list. Put each separate item on a new line."
    task_names = message.split("\n")
    with Db() as db:
        db.add_owner(owner_id, owner_name)
        task_ids = db.add_tasks(task_names, owner_id)
        db.new_list(task_ids, owner_id)
        task_list = db.get_tasks(task_ids)
    return f"Created a new list for {owner_name}\n" + print_task_list(task_list)


def show_list(context, owner_id, owner_name, message):
    with Db() as db:
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def add_tasks(context, owner_id, owner_name, message):
    with Db() as db:
        task_list = get_list_items(db, owner_id, owner_name)
        new_row_ids = db.add_tasks(message.split("\n"), owner_id)
        db.update_list_items(task_list + new_row_ids, owner_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def remove_tasks(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        for item in message.split("\n"):
            task_id = find_task_id_in_list(db, task_ids, item)
            task_ids.remove(task_id)
        db.update_list_items(task_ids, owner_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def top(context, owner_id, owner_name, message):
    return _reorder_task(owner_id, owner_name, message, 1)


def bottom(context, owner_id, owner_name, message):
    return _reorder_task(owner_id, owner_name, message, -1)


def move(context, owner_id, owner_name, message):
    m = match(r'^(.*) (\d+)$', message)
    if not m:
        return "Sorry, I don't understand. Accepted format: ~move <item> <position>"
    return _reorder_task(owner_id, owner_name, m.group(1).strip('"'), int(m.group(2)))


def _reorder_task(owner_id: int, owner_name: str, item: str, position: int):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        task_id = find_task_id_in_list(db, task_ids, item)
        task_ids.remove(task_id)
        if position == -1:
            task_ids.append(task_id)
        else:
            task_ids.insert(position - 1, task_id)
        db.update_list_items(task_ids, owner_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def start_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) == "STARTED":
            return "That task is already started."
        if "STARTED" in db.get_task_states(task_ids):
            return "You can only have one started task at a time."
        db.start_task(task_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def stop_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "STARTED":
            return "That task hasn't been started."
        db.stop_task(task_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def check_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) == "CHECKED":
            return "That task hasn't been started."
        db.complete_task(task_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def check_all(context, owner_id, owner_name, message):
    with Db() as db:
        list_items = get_list_items(db, owner_id, owner_name)
        tasks = message.split(" ")
        if not all([s.isdigit() for s in tasks]):
            return "All arguments must be positions of tasks, not names."
        task_ids = []
        for task in tasks:
            task_id = find_task_id_in_list(db, list_items, task)
            if db.get_task_state(task_id) == "CHECKED":
                return f"Task {task} has already been finished."
            task_ids.append(task_id)
        for task_id in task_ids:
            db.complete_task(task_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def uncheck_task(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        task_id = find_task_id_in_list(db, task_ids, message)
        if db.get_task_state(task_id) != "CHECKED":
            return "That task hasn't been completed."
        db.uncomplete_task(task_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)


def task_time(content, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        tasks = db.get_tasks(task_ids)
        output = f"{owner_name} times\n"
        for t in tasks:
            output += f"{t['name']}: {pretty_task_time(t['time_spent_sec'])}\n"
        output += f"\nTotal time: {pretty_task_time(sum([t['time_spent_sec'] for t in tasks]))}"
    return output


def clear_checked_tasks(context, owner_id, owner_name, message):
    with Db() as db:
        task_ids = get_list_items(db, owner_id, owner_name)
        task_states = db.get_task_states(task_ids)
        tasks = zip(task_ids, task_states)
        unchecked_tasks = []
        for task_id, state in tasks:
            if state != "CHECKED":
                unchecked_tasks.append(task_id)
        db.update_list_items(unchecked_tasks, owner_id)
        task_list = db.get_tasks(get_list_items(db, owner_id, owner_name))
    return f"{owner_name}'s list\n" + print_task_list(task_list)
