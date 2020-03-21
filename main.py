#!/usr/bin/env python3

from assets import tetrominoes
from random import choice
from time import sleep

import curses
import sys

WALL_CHAR = "#"

BLOCK_CHAR = "X"
BLOCK_WIDTH = 4

CONFIG_KEY_LEFT = "a"
CONFIG_KEY_DOWN = "s"
CONFIG_KEY_RIGHT = "d"
CONFIG_KEY_ROTATE_LEFT = "q"
CONFIG_KEY_ROTATE_RIGHT = "e"
CONFIG_KEY_ROTATE_QUIT = "x"


def draw_field(window):
    for y in range(5, 21):
        window.addch(y, 15, WALL_CHAR)
        window.addch(y, 27, WALL_CHAR)
    else:
        window.addstr(y, 15, WALL_CHAR * 12)



def draw_piece(piece, rotation, width, offset_x, offset_y, window):
    # loop over all points in the list
    w = width
    for i in range(0, len(piece)-1):
        y = i // w
        x = i % w

        window.addch(0, 0, str(rotation))

        # Alternate algorithms
        # 90°  idx w * (w-1) + y - w * x
        # 180° idx w * w - 1 - w * y - x
        # 270° idx w - 1 - y + w * x
        idx = [
            y * w + x,
            (w - 1 - x) * w + y,            # new_x = y; new_y = width - 1 - x; idx = new_y * width + new_x
            (w - 1 - y) * w + (w - 1 - x),  # new_x = w - 1 - x; new_y = w - 1 - y; idx = new_y * width + new_x
            x * w + (w-1) - y               # new_x = (width - 1) - y; new_y = x; idx = new_y * width + new_x      
        ][rotation]

        # cleaner rotation
        if rotation == 2:
            y -= 1
        if rotation == 3:
            x += 1

        x += offset_x
        y += offset_y
        if piece[idx] == 1:
            # curses uses y, x
            window.addch(y, x, BLOCK_CHAR)


def main(stdscr):
    stdscr.timeout(50)

    stdscr.keypad(1)

    # invisible cursor
    curses.curs_set(0)

    # initial screen
    stdscr.clear()

    # random block
    piece = choice(tetrominoes.blocklist)
    rotation, offset_x, offset_y = 0, 20, 5

    # game loop
    while True:
        try:
            key = stdscr.getkey()

            if key == CONFIG_KEY_ROTATE_LEFT:
                rotation -= 1
            if key == CONFIG_KEY_ROTATE_RIGHT:
                rotation += 1
            if key == CONFIG_KEY_LEFT:
                offset_x -= 1
            if key == CONFIG_KEY_DOWN:
                offset_y += 1
            if key == CONFIG_KEY_RIGHT:
                offset_x += 1
            if key == CONFIG_KEY_ROTATE_QUIT:
                break
            if key == "c":
                offset_x = 20
                offset_y = 5
                rotation = 0
                piece = choice(tetrominoes.blocklist)

            if rotation < 0:
                rotation = 3
            if rotation > 3:
                rotation = 0
        except:
            pass

        stdscr.erase()
        draw_field(stdscr)
        draw_piece(piece, rotation, BLOCK_WIDTH, offset_x, offset_y, stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
