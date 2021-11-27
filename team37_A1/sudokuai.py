#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from copy import deepcopy


from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def check_square(self, game_state, i, j, value):
        rows = game_state.board.m
        columns = game_state.board.n
        for p in range(((i - 1) * rows), (i * rows)):
            for q in range(((j - 1) * columns), (j * columns)):
                if game_state.board.get(p, q) == value:
                    return False
        return True

    def check_column(self, game_state, N, j, value):
        for p in range(N):
            if game_state.board.get(p, j) == value:
                return False
        return True

    def check_row(self, game_state, N, i, value):
        for q in range(N):
            if game_state.board.get(i, q) == value:
                return False
        return True

    # Check whether a turn is possible:
    # - the position of the board is non-empty
    # - the particular value to be inserted in the empty board position is not in the list of taboo moves
    # (DONE) - the value to be entered is not already included in the section
    # (DONE) - the value to be entered is not already in the same row
    # (DONE) - the value to be entered is not already in the same column

    def possible_move(self, game_state, i, j, value, rows, columns):
        # compute which of the squares on the board the current position is in
        introw = math.ceil((i + 1) / rows)
        intcol = math.ceil((j + 1) / columns)
        N = game_state.board.N
        if not (self.check_column(game_state, N, j, value) == self.check_row(game_state, N, i, value) ==
                self.check_square(game_state, introw, intcol, value) == True):
            return False
        else:
            return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j,
                                                                                     value) in game_state.taboo_moves

    def get_all_moves(self, game_state: GameState):
        N = game_state.board.N

        rows = game_state.board.m
        columns = game_state.board.n

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if
                     self.possible_move(game_state, i, j, value, rows, columns)]

        return all_moves

    def update_taboo_moves(self, game_state:GameState):
        taboo_moves = []
        if len(game_state.moves) > 0:
            last_move = game_state.moves[-1]
            i = last_move.i
            j = last_move.j
            value = last_move.value
            N = game_state.board.N
            rows = game_state.board.m
            columns = game_state.board.n

            for _j in range(N):
                taboo_move = Move(i, _j, value)
                if not self.possible_move(game_state, i, _j, value, rows, columns):
                    taboo_moves.append(taboo_move)
            for _i in range(N):
                taboo_move = Move(_i, j, value)
                if not self.possible_move(game_state, _i, j, value, rows, columns):
                    taboo_moves.append(taboo_move)

        if game_state.taboo_moves:
            taboo_moves = game_state.taboo_moves + taboo_moves
        else:
            taboo_moves = taboo_moves
        return taboo_moves

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:   
        #all_moves = self.get_all_moves(game_state)
        
        #while True:
        #    time.sleep(0.2)
        #    self.propose_move(random.choice(all_moves))
        depth = 1
        while True:
            self.propose_move(self.alphabeta(game_state, None, True, depth, math.inf, -math.inf)[0])
            depth = depth + 1
    
    #TODO to improve the amount of data passed each time, exchange game_state with a combination of board and all_moves list
    # update all_moves and board before passing along a new instance for the next call
    def alphabeta(self, game_state: GameState, last_move: Move, maximizing_player: bool, depth, alpha, beta) -> (Move, int):
        #get a list of all possible moves using the input gamestate
        all_moves = self.get_all_moves(game_state)
        #is this the final level to consider?
        if depth == 0 or len(all_moves) == 0:
            #TODO: heuristic function to evaluate current board (based on last move)
            #add a case for original lastmove being NULL on first call (in case depth = 0 is set)
            return None, 0
        #not the final move, check if maximizing player
        if maximizing_player:
            #start with -infty
            best_value = -math.inf
            best_move = random.choice(all_moves)
            for move in all_moves:
                #update new gamestate
                new_gs = deepcopy(game_state)
                new_gs.board.put(move.i, move.j, move.value)
                new_gs.moves.append(move)
                new_value = max(best_value, self.alphabeta(new_gs, move, False, depth - 1, alpha, beta)[1])
                # compare to beta to check for breakoff
                if new_value >= beta:
                    break
                # update alpha if allowed to continue
                alpha = max(alpha, new_value)
                # update best move and global value to the new move as long as it is at least as good as the previous best
                if new_value >= best_value:
                    best_value = new_value
                    best_move = move
            #after the loop, return the best move and its associated value
            return best_move, best_value
        else:
            # minimizing player start with infty
            best_value = math.inf
            best_move = all_moves[0]
            for move in all_moves:
                #update new gamestate
                new_gs = deepcopy(game_state)
                new_gs.board.put(move.i, move.j, move.value)
                new_gs.moves.append(move)
                new_value = min(best_value, self.alphabeta(new_gs, move, True, depth - 1, alpha, beta)[1])
                # compare the alpha to check for breakoff
                if new_value <= alpha:
                    break
                #update beta if allowed to continue
                beta = max(beta, new_value)
                #update best move and global value to the new move as long as it is at least as good as the previous best
                if new_value <= best_value:
                    best_value = new_value
                    best_move = move
            #after the loop, return the best move and its associated value
            return best_move, best_value
            
    def evaluate_board(self, board: SudokuBoard, last_move: Move) -> int:
        #check whether the board is the original board and no move was performed
        if last_move == None:
            #evaluate naively whether the state of the board is good by counting a score based on the number of filled in slots per section on the board
            rows_count = board.n
            cols_count = board.m
            total_score = 0
            for r in range(1, rows_count+1):
                for c in range(1, cols_count+1):
                    #we're at some section of the board positioned as (r,c) in the bottom right corner
                    score_section = 0
                    for p in range(((r - 1) * rows_count), (r * rows_count)):
                        for q in range(((c - 1) * cols_count), (c * cols_count)):
                            #we now have a singular number in the section denoted by (r,c) in position (p, q) of the board
                            if not (board.get(p, q) == SudokuBoard.empty):
                                score_section = score_section + 1
                    total_score = total_score + score_section
            return total_score
        else:
            #a move was made
            #TODO implement more defined heuristic based on recent move
            
            
            #TEMPORARY:
            rows_count = board.n
            cols_count = board.m
            total_score = 0
            for r in range(1, rows_count+1):
                for c in range(1, cols_count+1):
                    #were at some section of the board positioned as (r,c) in the bottom right corner
                    score_section = 0
                    for p in range(((r - 1) * rows_count), (r * rows_count)):
                        for q in range(((c - 1) * cols_count), (c * cols_count)):
                            #we now have a singular number in the section denoted by (r,c) in position (p, q) of the board
                            if not (board.get(p, q) == SudokuBoard.empty):
                                score_section = score_section + 1
                    total_score = total_score + score_section
            return total_score
        return 0
        
        
        
        
        