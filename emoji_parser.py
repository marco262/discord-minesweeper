# ||:one:|| ||:two:|| ||:three:|| ||:four:|| ||:five:|| ||:six:|| ||:seven:|| ||:eight:|| ||:bomb:|| ||:white_large_square:||

emoji_dict = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    0: "white_large_square",
    "B": "boom"
}


def grid_to_emoji(grid):
    return "\n".join([" ".join([f"||:{emoji_dict[c]}:||" for c in row]) for row in grid])
