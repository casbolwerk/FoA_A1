import math


from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove


class Metadata(object):
    """A Metadata object is a tuple (last_move, best_move, best_score) that represents some global and local information
    for the turn computation as well as the sub-tree computation."""

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

    def set(self, last_move: Move, best_move: Move, best_score: int):
        """
        Update the values of the full Metadata object
        @param last_move: The move with which to replace the current last_move
        @param best_move: The move with which to replace the current best_move
        @param best_score: The score with which to replace the current best_score, which belongs to the new best_move
        @return:
        """
        self.last_move = last_move
        self.best_move = best_move
        self.best_score = best_score

    def setLast(self, new_last: Move):
        """
        Update the last_move of the Metadata object
        @param new_last: The move with which to replace the current last_move
        @return:
        """
        self.last_move = new_last