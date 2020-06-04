#!/usr/bin/env python
# encoding: utf-8

import numpy as np

import shutil

from enum import Enum
from dataclasses import dataclass
from random import randint
from time import sleep


class Misc:
    _base = '\u001b['
    _pos = '\033['
    
    reset = f'{_base}0m'
    red_bg = f'{_base}41m'
    clear = f'{_base}2J'


class CellState(Enum):
    '''
    The cell states
        DEAD: 
        ALIVE:
    '''
    DEAD = 0
    ALIVE = 1


class BoardState(Enum):
    '''
    The board states
        STALE: no change is possible
        REPETITIVE: There are repeating patterns (e.g. spaceships, oscillators, etc.)
        ACTIVE: There are still live cells, and new emerging patterns
    '''
    STALE = 0
    REPETITIVE = 1
    ACTIVE = 2


class Game:
    ''' Conway's game of life '''

    def __init__(self, rows, cols):
        '''
        Initialise the grids

        :param rows: grids rows
        :param cols: grids columns
        '''
        self.cells = np.full((rows, cols), CellState.DEAD)
        self.buffer = np.copy(self.cells)

        self.current_gen = 0
        self.board_state = BoardState.ACTIVE

        # Save the different states of the cells
        self.generations = {
            'meta': {
                'rows': rows,
                'cols': cols
            }
        }


    def setRandom(self):
        '''
        Change all values in the grid (cell's states)
        '''
        rows, cols = self.cells.shape

        self.cells = np.array([
            np.random.choice([CellState.DEAD, CellState.ALIVE], cols)
            for _ in range(rows)
        ])

        self.buffer = np.copy(self.cells)


    def setAt(self, row, col, state):
        '''
        Change cell's value

        :param row: the row where the cell stands
        :param col: the column where the cell stands
        :param state: the state which the cell will have
        '''
        self.cells[row, col] = state


    def display(self):
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

        string += f'Generation: { self.current_gen }'

        print(string)


    def setNextCellState(self, row, col):
        '''
        Set the next state for a cell

        :param row: the row where the cell stands
        :param col: the column where the cell stands
        '''
        rows, cols = self.cells.shape

        # Get the neighbor rows for the cell
        start_row, end_row = row - 1, row + 2
        if start_row < 0: start_row = 0
        if end_row > rows: end_row = rows

        # Get the neighbor columns for the cell
        start_col, end_col = col - 1, col + 2
        if start_col < 0: start_col = 0
        if end_col > cols: end_col = cols

        # Extract only the cells which are neighbors (contains the current cell)
        cells = self.cells[start_row:end_row, start_col:end_col]

        # Number of live neighbors (contains the state of the current cell)
        alive_cells = np.sum(cells == CellState.ALIVE)

        if self.cells[row, col] == CellState.ALIVE:
            # If the current cell is alive decrement alive_cells
            alive_cells -= 1

            # Set state to DEAD if the cell doesn't have 2 or 3 live neighbors
            if alive_cells != 2 and alive_cells != 3:
                self.buffer[row, col] = CellState.DEAD
        else:
            # Set the state to ALIVE if the cell has exactly 3 live neighbors
            if alive_cells == 3:
                self.buffer[row, col] = CellState.ALIVE


    def setNextState(self):
        ''' Set the state for all cells after a single iteration '''
        rows, cols = self.cells.shape

        np.copyto(self.buffer, self.cells)

        for row in range(rows):
            for col in range(cols):
                self.setNextCellState(row, col)
    
        # Hash the current array
        data = self.buffer.tostring()
        hashed = hash(data)

        # Check if the current generation has already happened
        if hashed not in self.generations.keys():
            self.generations[hashed] = {
                'data': data,
                'generation': self.current_gen
            }
            self.current_gen += 1
        else:
            self.board_state = BoardState.REPETITIVE

        np.copyto(self.cells, self.buffer)


    def start(self):
        current_gen = 0

        while current_gen < self.gens and CellState.ALIVE in self.cells and not self.isStale():
            self.display(current_gen)
            self.setNextState()
            sleep(.08)


    def startUntilEmpty(self):
        current_gen = 0

        while CellState.ALIVE in self.cells and self.board_state == BoardState.ACTIVE:
            self.display()
            self.setNextState()

            sleep(.09)
 

if __name__ == '__main__':
    rows = 20
    cols = 40
    
    game = Game(rows, cols)
    game.setRandom()

    game.startUntilEmpty()
