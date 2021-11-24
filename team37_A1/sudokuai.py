#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math


from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()


    # Create a set of all moves that are valid given the board state and the list of taboo moves.
    def get_all_moves(self, game_state: GameState):
        N = game_state.board.N
        
        rows = game_state.board.m
        columns = game_state.board.n
        
        def check_square(i, j, value):
            for p in range(((i-1)*rows), (i*rows)):
                for q in range(((j-1)*columns), (j*columns)):
                    if game_state.board.get(p, q) == value:
                        return False
            return True
        
        def check_column(j, value):
            for p in range(N):
                if game_state.board.get(p, j) == value:
                    return False
            return True
        
        def check_row(i, value):
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
        def possible(i, j, value):
            #compute which of the squares on the board the current position is in
            introw = math.ceil((i+1)/rows)
            intcol = math.ceil((j+1)/columns)
            if not (check_column(j, value) == check_row(i, value) == check_square(introw, intcol, value) == True):
                return False
            else:
                return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves 

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]

        return all_moves

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:        
        all_moves = self.get_all_moves(game_state)

        move = random.choice(all_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))
            
#        player_number = 1 if len(game_state.moves) % 2 == 0 else 2
#        move, _ = self.minimax(game_state, player_number, True, 8, -math.inf, math.inf)
#        self.propose_move(move)
#        while True:
#            time.sleep(0.2)

#            upd_game_state = game_state
#            upd_player_number = 1 if len(upd_game_state.moves) % 2 == 0 else 2
#            move, _ = self.minimax(upd_game_state, upd_player_number, True, 8, -math.inf, math.inf)
#            self.propose_move(move)

    def max(self, game_state: GameState, all_moves, player_number, depth, alpha, beta) -> (Move, int):
        max_score = -1*math.inf
        best_move = all_moves[0]
        for move in all_moves:
            temp_game_state = game_state
            i = move.i
            j = move.j
            value = move.value
            curr_board = temp_game_state.board
            curr_board.put(i, j, value)
            temp_game_state.board = curr_board
            temp_game_state.moves.append(move)

            curr_score = self.minimax(temp_game_state, player_number, False, depth - 1, alpha, beta)[1]

            if curr_score > max_score:
                max_score = curr_score
                best_move = move

            alpha = max(alpha, curr_score)
            if beta <= alpha:
                break

        return best_move, max_score

    def min(self, game_state: GameState, all_moves, player_number, depth, alpha, beta) -> (Move, int):
        min_score = math.inf
        best_move = all_moves[0]
        for move in all_moves:
            temp_game_state = game_state
            i = move.i
            j = move.j
            value = move.value
            curr_board = temp_game_state.board
            curr_board.put(i, j, value)
            temp_game_state.board = curr_board
            temp_game_state.moves.append(move)

            curr_score = self.minimax(temp_game_state, player_number, True, depth - 1, alpha, beta)[1]

            if curr_score < min_score:
                min_score = curr_score
                best_move = move

            beta = min(beta, curr_score)
            if beta <= alpha:
                break

        return best_move, min_score

    # eventual parameters board_copy, depth - 1, alpha, beta, player
    def minimax(self, game_state: GameState, player_number, maximizing_player: bool, depth, alpha, beta) -> Move:
        '''
        Minimax algorithm with alpha-beta pruning.
        @param game_state: A Sudoku game state, with board and moves.
        @param player_number: A player number, either 1 or 2.
        @param depth: (Remaining) depth of the minimax algorithm.
        @param alpha: The alpha in alpha-beta pruning.
        @param beta: The beta in alpha-beta pruning.
        @return: The move that the current player should play.
        '''
        all_moves = self.get_all_moves(game_state)
        max_moves = game_state.initial_board.squares.count(SudokuBoard.empty)
        number_of_moves = len(game_state.moves)
        print(number_of_moves, max_moves)
        print(game_state)
        print('all_moves', len(all_moves))

        if depth == 0 or not (len(all_moves) > 0) or number_of_moves >= max_moves:
            print(depth == 0, not len(all_moves) > 0, number_of_moves < max_moves)
            print('\r[MiniMax] Ending minimax..')
            return None, game_state.scores[player_number-1]

        if maximizing_player:
            print('\r[MiniMax] Maximizing player')
            best_move, score = self.max(game_state, all_moves, player_number, depth, alpha, beta)
            print(best_move, score)
        else:
            print('\r[MiniMax] Minimizing player')
            best_move, score = self.min(game_state, all_moves, player_number, depth, alpha, beta)

        return best_move, score

