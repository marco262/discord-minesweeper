from src.db.db import Db
from src.utils import print_task_list, find_task_id_in_list, NoItemsFoundException, MultipleItemsFoundException


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
            try:
                task_id = find_task_id_in_list(db, task_ids, item)
            except NoItemsFoundException:
                return f'Couldn\'t find any list item matching "{item}"'
            except MultipleItemsFoundException as e:
                return f'Multiple items found matching "{item}":\n' + "\n".join(e.args[0])
            print(task_id)
            task_ids.remove(task_id)
        db.update_list_items(task_ids, owner_id)
        task_list = db.get_tasks(db.get_list_items(owner_id))

    return f"{owner_name}'s list\n" + print_task_list(task_list)
