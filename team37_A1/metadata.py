import math


from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove


class Metadata(object):
    """A Move is a tuple (i, j, value) that represents the action board.put(i, j, value) for a given
    sudoku configuration board."""

    def __init__(self, last_move: Move, best_move: Move, best_score: int):
        """
        Constructs a move.
        @param last_move: the last move executed on the root node of the sub-tree
        @param best_move: the best move found during the current turn computation
        @param best_score: the best score found (for the best move) during the current turn computation
        """
        self.last_move = last_move
        self.best_move = best_move
        self.best_score = best_score
    #
    # def __str__(self):
    #     return f'({self.i},{self.j}) -> {self.value}'
    #
    # def __eq__(self, other):
    #     return (self.i, self.j, self.value) == (other.i, other.j, other.value)
