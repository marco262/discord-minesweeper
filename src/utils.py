icons = {
    "NOT_STARTED": ":white_large_square:",
    "STARTED": ":arrow_forward",
    "CHECKED": ":white_check_mark:"
}


def get_icon(task):
    return icons[task["state"]]


def print_task_list(task_list):
    output = []
    for i, task in enumerate(task_list):
        output.append(f"{get_icon(task)} {task['name']}    ({i + 1})")
    return "\n".join(output)
