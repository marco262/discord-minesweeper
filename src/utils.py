from typing import List

from src.db.db import Db

icons = {
    "NOT_STARTED": ":white_large_square:",
    "STARTED": ":arrow_forward:",
    "CHECKED": ":white_check_mark:"
}


def get_icon(task):
    return icons[task["state"]]


def print_task_list(task_list):
    output = []
    for i, task in enumerate(task_list):
        output.append(f"{get_icon(task)} {task['name']}    ({i + 1})")
    return "\n".join(output)


def find_task_id_in_list(db: Db, task_ids: List[int], item: str) -> int:
    """
    :param db:
    :param item:
    :return:
    """
    if item.isdigit():
        return task_ids[int(item) - 1]
    else:
        filtered_task_ids = db.filter_task_ids_by_name(task_ids, item)
        if len(filtered_task_ids) == 0:
            raise ListBotError(f"Couldn't find any list item matching \"{item}\"")
        if len(filtered_task_ids) > 1:
            task_names = db.get_task_names(filtered_task_ids)
            raise ListBotError(f"Multiple items found matching \"{item}\":\n" + "\n".join(task_names))
        return filtered_task_ids[0]


def pretty_task_time(secs: int) -> str:
    if secs < 60:
        return f"{secs}s"
    if secs < 3600:
        return f"{int(secs / 60)}m{secs % 60}s"
    return f"{int(secs / 3600)}h{int(secs % 3600 / 60)}m{secs % 60}s"


class ListBotError(Exception):
    pass
