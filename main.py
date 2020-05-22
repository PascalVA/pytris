#!/usr/bin/env python3

from random import choice
from time import sleep
from copy import copy
from playsound import playsound

import curses
import sys

from assets import tetrominoes
from multiprocessing import Process
from os import path
from random import shuffle

DEBUG = False

BLOCK_CHAR = "█"
WALL_CHAR = "█"

CONFIG_KEY_UP = "w"
CONFIG_KEY_LEFT = "a"
CONFIG_KEY_DOWN = "s"
CONFIG_KEY_RIGHT = "d"
CONFIG_KEY_ROTATE_LEFT = "q"
CONFIG_KEY_ROTATE_RIGHT = "e"
CONFIG_KEY_HOLD_BLOCK = "c"
CONFIG_KEY_PAUSE = "p"
CONFIG_KEY_QUIT = "n"


class Area(object):

    def __init__(self):
        self.area = []
        self.width = 12
        self.height = 18
        self.offset_x = 0
        self.offset_y = 0

        # generate playable area
        self.area = []
        for idx in range(0, (self.width * self.height)):
            if (idx + 1) % self.width == 0 \
                    or idx % self.width == 0 \
                    or idx // self.width == self.height - 1:
                self.area.append(9)
            else:
                self.area.append(0)

    def get_point(self, x, y):
        idx = y * self.width + x
        return self.area[idx]

    def get_points(self):
        for i in range(0, len(self.area)):
            y = i // self.width
            x = i % self.width
            yield x, y


def blank_line(area):
    return [9] + ([0] * (area.width - 2)) + [9]


def flash_lines(area, lines, screen_offset_x, screen_offset_y, window):
    for i in [3, 0, 3]:
        for y in lines:
            start = y * area.width + 1
            end = start + area.width - 2
            area.area[start:end] = [i] * (area.width - 2)
        # HACK: draw outside of game loop
        # TODO: ? drawing to screen does not work here
        window.erase()
        draw(area, screen_offset_x, screen_offset_y, window)


def fits(block, area, offset_x, offset_y, rotation):
    _block = copy(block)
    _block.rotate(rotation)
    for x, y in _block.get_points():
        # project new block position for point on area
        area_x = x + _block.offset_x + offset_x
        area_y = y + _block.offset_y + offset_y
        # don't check out of bounds
        if area_y > area.height - 1:
            continue

        block_value = _block.get_point(x, y)
        area_value = area.get_point(area_x, area_y)

        # if any of the points overlap, return False
        if block_value > 0 and area_value > 0:
            return False

    return True


def register_block(block, area):
    # write block to area
    for x, y in block.get_points():
        area_x = x + block.offset_x
        area_y = y + block.offset_y
        # don't check out of bounds
        if area_y > area.height - 1:
            continue

        block_value = block.get_point(x, y)
        if block_value > 0:
            idx = area_y * area.width + area_x
            area.area[idx] = block.get_point(x, y)

    # check for lines
    lines = []
    for y in range(block.offset_y, block.offset_y + 4):
        if y < area.height - 1:
            start = y * area.width + 1
            end = start + area.width - 2
            if min(area.area[start:end]):
                 lines.append(y)
    return lines


def draw(asset, screen_offset_x, screen_offset_y, window):
    # loop over all points in the asset area
    w = asset.width
    for x, y in asset.get_points():
        value = asset.get_point(x, y) 

        # handle screen offsets
        x = x + screen_offset_x + asset.offset_x
        y = y + screen_offset_y + asset.offset_y

        # curses uses y, x
        if value == 9:
            window.addch(y, x, WALL_CHAR)
        elif value == 0:
            pass
        else:
            window.addch(y, x, BLOCK_CHAR, curses.color_pair(value))


def main(stdscr):
    # screen setup
    stdscr.timeout(100)
    stdscr.keypad(1)    # handle escape chars
    curses.curs_set(0)  # invisible cursor
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.clear()

    counter = 0
    pause = False
    score = 0

    # area
    area = Area()

    # contains the block the user put in hold
    held_block = None

    # first block
    next_block = choice(tetrominoes.blocklist)()
    new_block = True

    # game loop
    while True:
        # draw offsets for the screen
        max_y, max_x = stdscr.getmaxyx()
        screen_offset_x = max_x // 2 - area.width // 2
        screen_offset_y = max_y //2 - area.height // 2

        if new_block:
            block = next_block
            # copy block without offsets for held_block
            block_copy = copy(block)
            if not fits(block, area, 0, 0, 0):
                break

            score += 25
            next_block = choice(tetrominoes.blocklist)()
            new_block = False

        # force block down
        if not pause and counter % 10 == 0:
            if fits(block, area, 0, +1, 0):
                block.move_y(+1)
            else:
                new_block = True

                lines = register_block(block, area)

                # remove cleared lines
                # TODO: there is probably a more elegant
                #       way to delete lines from the area
                if lines:
                    # animation
                    flash_lines(area, lines, screen_offset_x, screen_offset_y, stdscr)

                    for y in lines:
                        start = y * area.width
                        end = start + area.width
                        del area.area[start:end]
                        area.area = blank_line(area) + area.area

                    if len(lines) == 4:
                        score += 1200
                    else:
                        score += (len(lines) * 100)

        counter += 1

        try:
            # handle user input
            key = stdscr.getkey()

            if not pause or DEBUG:
                if key == CONFIG_KEY_ROTATE_LEFT:
                    if fits(block, area, 0, 0, -1):
                        block.rotate(-1)
                if key == CONFIG_KEY_ROTATE_RIGHT:
                    if fits(block, area, 0, 0, +1):
                        block.rotate(+1)
                if key == CONFIG_KEY_LEFT:
                    if fits(block, area, -1, 0, 0):
                        block.move_x(-1)
                if key == CONFIG_KEY_DOWN:
                    if fits(block, area, 0, +1, 0):
                        block.move_y(+1)
                if key == CONFIG_KEY_RIGHT:
                    if fits(block, area, +1, 0, 0):
                        block.move_x(+1)
                if key == CONFIG_KEY_HOLD_BLOCK:
                    if held_block is None:
                        held_block = copy(block_copy)
                        new_block = True
                    else:
                        held_block, block = (copy(block_copy), copy(held_block))
                        block_copy = copy(block)

            if key == CONFIG_KEY_PAUSE:
                pause = not pause
            if key == CONFIG_KEY_QUIT:
                break

            if DEBUG:
                if key == CONFIG_KEY_UP:
                    if fits(block, area, 0, +1, 0):
                        block.move_y(-1)
                if key == "v":
                    new_block = True
        except:
            pass

        #
        # screen output
        #

        stdscr.erase()
        # screen
        draw(area, screen_offset_x, screen_offset_y, stdscr)
        # block
        draw(block, screen_offset_x, screen_offset_y, stdscr)
        # score
        stdscr.addstr(screen_offset_y, screen_offset_x + 15, f"Score: {score}")
        if held_block is not None:
            draw(held_block, screen_offset_x - 10, screen_offset_y, stdscr)
        # next block
        stdscr.addstr(screen_offset_y + 2, screen_offset_x + 15, "Next block:")
        draw(next_block, screen_offset_x + 10, screen_offset_y + 4, stdscr)
        # pause
        stdscr.addstr(screen_offset_y + 10, screen_offset_x + 15, "GAME PAUSED" if pause else "")
        # debug
        stdscr.addstr(screen_offset_y + 15, screen_offset_x + 15, f"R {block.rotation}")

    return score


def background_music():
    """playsound on linux does not yet support non-blocking play
    """
    playlist = list(
        filter(
            lambda f: path.exists(f),
            ['assets/typea.mp3', 'assets/typeb.mp3', 'assets/typec.mp3'])
    )
    if not playlist:
        return
    shuffle(playlist)
    while True:
        for i in playlist:
            try:
                playsound(i)
            except:
                pass


if __name__ == "__main__":
    p = Process(target=background_music)
    p.start()
    score = curses.wrapper(main)
    print(f"GAME OVER - Your score was: {score}")
    p.kill()
