from random import randint

from src.minesweeper.emoji_parser import grid_to_emoji

WIDTH = 10
HEIGHT = 10
BOMBS = 10


def empty_grid(width, height):
    grid = []
    for _ in range(height):
        grid.append([0] * width)
    return grid


def add_bomb(grid, x, y):
    if grid[y][x] == "B":
        return False
    grid[y][x] = "B"
    increment_space(grid, x - 1, y - 1)
    increment_space(grid, x, y - 1)
    increment_space(grid, x + 1, y - 1)
    increment_space(grid, x - 1, y)
    increment_space(grid, x + 1, y)
    increment_space(grid, x - 1, y + 1)
    increment_space(grid, x, y + 1)
    increment_space(grid, x + 1, y + 1)
    return True


def increment_space(grid, x, y):
    if x < 0 or y < 0:
        return
    try:
        if grid[y][x] == "B":
            return
        grid[y][x] += 1
    except IndexError:
        pass


def print_grid(grid):
    print("\n".join([" ".join([str(c) for c in row]) for row in grid]))


def build_game(width, height, bombs):
    grid = empty_grid(width, height)

    bomb_count = bombs
    retry_count = 0
    while bomb_count > 0:
        if add_bomb(grid, randint(0, width - 1), randint(0, height - 1)):
            bomb_count -= 1
            retry_count = 0
        else:
            retry_count += 1
        if retry_count > 10:
            raise RecursionError(f"Too many retries: width=f{width}, height={height}, bombs={bombs}")

    return grid


def new_game(width=None, height=None, bombs=None):
    if width is None:
        width = WIDTH
    if height is None:
        height = HEIGHT
    if bombs is None:
        bombs = BOMBS

    grid = build_game(width, height, bombs)
    return f"{width}x{height} with {bombs} bombs\n" + grid_to_emoji(grid)


if __name__ == "__main__":
    new_game()
