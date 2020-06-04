#!/usr/bin/env python
# encoding: utf-8

import numpy as np

import shutil

from enum import Enum
from random import randint
from time import sleep


class CellState(Enum):
    DEAD = 0
    ALIVE = 1


class BoardState(Enum):
    STALE = 0
    ACTIVE = 1


class Game:
    def __init__(self, rows, cols, gens):
        self.cells = np.full((rows, cols), CellState.DEAD)
        self.buffer = np.copy(self.cells)

        self.board_state = BoardState.ACTIVE

        self.gens = gens


    def setRandom(self):
        rows, cols = self.cells.shape

        self.cells = np.array([
            np.random.choice([CellState.DEAD, CellState.ALIVE], cols)
            for _ in range(rows)
        ])

        self.buffer = np.copy(self.cells)


    def setAt(self, row, col, state):
        self.cells[row, col] = state


    def setGens(self, gens):
        self.gens = gens


    def display(self, gen = 0):
        term_cols, term_rows = shutil.get_terminal_size((80, 20))
        rows, cols = self.cells.shape

        start_at_col = (term_cols // 2) - (cols // 2)
        start_at_row = (term_rows // 2) - (rows // 2)

        _base = '\u001b['
        _pos = '\033['
        
        red_bg = f'{_base}41m'
        reset = f'{_base}0m'
        clear = f'{_base}2J'

        print(clear)
        print(f'{_pos}2H')

        string = ''

        for row in range(rows):
            string += ' ' * (start_at_col)
            for col in range(cols):
                string += f'{red_bg}  {reset}' if self.cells[row, col] == CellState.ALIVE else '  '
            string += '\n'

        string += f'Generation: { gen }'

        print(string)


    def _setNextState(self, row, col):
        rows, cols = self.cells.shape

        start_row, end_row = row - 1, row + 2
        if start_row < 0: start_row = 0
        if end_row > rows: end_row = rows

        start_col, end_col = col - 1, col + 2
        if start_col < 0: start_col = 0
        if end_col > cols: end_col = cols

        cells = self.cells[start_row:end_row, start_col:end_col]
        alive_cells = np.sum(cells == CellState.ALIVE)

        if self.cells[row, col] == CellState.ALIVE:
            alive_cells -= 1

            if alive_cells != 2 and alive_cells != 3:
                self.buffer[row, col] = CellState.DEAD
        else:
            if alive_cells == 3:
                self.buffer[row, col] = CellState.ALIVE


    def setNextState(self):
        rows, cols = self.cells.shape

        np.copyto(self.buffer, self.cells)

        for row in range(rows):
            for col in range(cols):
                self._setNextState(row, col)

        if (self.cells == self.buffer).all():
            self.board_state = BoardState.STALE

        np.copyto(self.cells, self.buffer)


    def isStale(self):
        return False


    def start(self):
        current_gen = 0

        while current_gen < self.gens and CellState.ALIVE in self.cells and not self.isStale():
            self.display(current_gen)
            self.setNextState()

            current_gen += 1

            sleep(.08)


    def startUntilEmpty(self):
        current_gen = 0

        while CellState.ALIVE in self.cells and self.board_state == BoardState.ACTIVE:
            self.display(current_gen)
            self.setNextState()

            current_gen += 1

            #sleep(.08)
            sleep(.09)
 

if __name__ == '__main__':
    rows = 40
    cols = 80
    
    game = Game(rows, cols, 40)
    game.setRandom()

    game.startUntilEmpty()
