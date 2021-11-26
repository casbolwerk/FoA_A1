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
        """
        Checks whether a certain value can be inserted in a specific block.
        @param game_state: The current state of the game
        @param i: "Row" of the square (note that this is a different interpretation of row, in terms of blocks)
        @param j: "Column" of the square (note that this is a different interpretation of column, in terms of blocks)
        @param value: The value that we wish to check for
        """
        rows = game_state.board.m
        columns = game_state.board.n
        for p in range(((i - 1) * rows), (i * rows)):
            for q in range(((j - 1) * columns), (j * columns)):
                if game_state.board.get(p, q) == value:
                    return False
        return True

    def check_column(self, game_state, N, j, value):
        """"
        Checks whether a certain value can be inserted in a specific column.
        @param game_state: The current state of the game
        @param N: The dimension of the board
        @param j: The column that we wish to check
        @param value: The value that we potentially want to insert
        """
        for p in range(N):
            if game_state.board.get(p, j) == value:
                return False
        return True

    def check_row(self, game_state, N, i, value):
        """"
        Checks whether a certain value can be inserted in a specific row.
        @param game_state: The current state of the game
        @param N: The dimension of the board
        @param i: The row that we wish to check
        @param value: The value that we potentially want to insert
        """
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
        """
        Checks whether a certain turn is possible, that is:
         - the position of the board is non-empty
         - the particular value to be inserted in the empty board position is not in the list of taboo moves
         - the value to be entered is not already included in the section
         - the value to be entered is not already in the same row
         - the value to be entered is not already in the same column
        @param game_state: The current state of the game
        @param i: The row in which the agent will possibly insert
        @param j: The column in which the agent will possibly insert
        @param value: The value which the agent wishes to insert
        @param rows: The # of rows (per block)
        @param columns: The # of columns (per block)
        @return: Boolean indicating whether the move is possible (=True) or not (=False)
        """
        # Compute which of the squares (or blocks) on the board the current position is in:
        introw = math.ceil((i + 1) / rows)
        intcol = math.ceil((j + 1) / columns)
        N = game_state.board.N
        if not (self.check_column(game_state, N, j, value)
                == self.check_row(game_state, N, i, value)
                == self.check_square(game_state, introw, intcol, value)
                == True):
            return False
        else:
            return game_state.board.get(i, j) == SudokuBoard.empty and not \
                TabooMove(i, j, value) in game_state.taboo_moves

    def get_all_moves(self, game_state: GameState):
        """
        Gets all the possible moves from the current state of the game.
        @param game_state: The current state of the game
        @return: A list with all possible moves
        """
        N = game_state.board.N

        rows = game_state.board.m
        columns = game_state.board.n

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if
                     self.possible_move(game_state, i, j, value, rows, columns)]

        return all_moves

    def update_taboo_moves(self, game_state: GameState):
        """
        Updates the list of taboo moves.
        @param game_state: The current state of the game
        @return: A list with the taboo moves
        """
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

        # Concatenate with the list of moves that were established to be taboo before
        if game_state.taboo_moves:
            taboo_moves = game_state.taboo_moves + taboo_moves
        else:
            taboo_moves = taboo_moves
        return taboo_moves

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        """
        Computes the best possible move from the given game state
        @param game_state: The current state of the game
        @return: The best possible move
        """
        # Get all possible moves
        all_moves = self.get_all_moves(game_state)

        # Find out whose turn it is
        player_number = 1 if len(game_state.moves) % 2 == 0 else 2

        # Retrieve the best possible move with the minimax algorithm
        move, _ = self.minimax(game_state, player_number, True, 4, -math.inf, math.inf)

        print('\r[MiniMax] FINAL MOVE:', move)
        print(game_state.initial_board)
        print(game_state.board)

        # Propose the move
        self.propose_move(move)


        # while True:
        #     time.sleep(0.2)

        #     upd_game_state = game_state
        #     upd_player_number = 1 if len(upd_game_state.moves) % 2 == 0 else 2
        #     move, _ = self.minimax(upd_game_state, upd_player_number, True, 8, -math.inf, math.inf)
        #     self.propose_move(move)

    def max(self, game_state: GameState, all_moves, player_number, depth, alpha, beta) -> (Move, int):
        """
        Calculates what the best move is, that is, the move which generates the highest score (value)
        (since the agent is the maximizing player).
        @param game_state: The current state of the game
        @param all_moves: A list with all possible moves
        @param player_number: A player number, either 1 or 2
        @param depth: (Remaining) depth of the minimax algorithm
        @param alpha: Alpha to be used in alpha-beta pruning
        @param beta: Beta to be used in alpha-beta pruning
        @return: The best move and score associated with it
        """
        max_score = -1*math.inf
        best_move = all_moves[0]
        # For every possible move find out what score would be associated with it
        for move in all_moves:
            temp_game_state = deepcopy(game_state)
            i = move.i
            j = move.j
            value = move.value
            curr_board = temp_game_state.board
            curr_board.put(i, j, value)
            temp_game_state.board = curr_board
            temp_game_state.moves.append(move)
            temp_game_state.taboo_moves = self.update_taboo_moves(game_state)

            curr_score = self.minimax(temp_game_state, player_number, False, depth - 1, alpha, beta)[1]

            print(curr_score)
            print(move)
            # If this score is better (higher) than the score associated with the best move we found so far, update it
            if curr_score > max_score:
                max_score = curr_score
                best_move = move

            alpha = max(alpha, curr_score)
            if beta <= alpha:
                break

        return best_move, max_score

    def min(self, game_state: GameState, all_moves, player_number, depth, alpha, beta) -> (Move, int):
        """
        Calculates what the best move is, that is, the move which generates the lowest score (value)
        (since the agent is the minimizing player).
        @param game_state: The current state of the game
        @param all_moves: A list with all possible moves
        @param player_number: A player number, either 1 or 2
        @param depth: (Remaining) depth of the minimax algorithm
        @param alpha: Alpha to be used in alpha-beta pruning
        @param beta: Beta to be used in alpha-beta pruning
        @return: The best move and score associated with it
        """
        min_score = math.inf
        best_move = all_moves[0]
        print([(move.i, move.j, move.value) for move in all_moves])
        # For every possible move find out what score would be associated with it
        for move in all_moves:
            print(move)
            temp_game_state = game_state
            i = move.i
            j = move.j
            value = move.value
            curr_board = temp_game_state.board
            curr_board.put(i, j, value)
            temp_game_state.board = curr_board
            temp_game_state.moves.append(move)

            print(temp_game_state.board)
            curr_score = self.minimax(temp_game_state, player_number, True, depth - 1, alpha, beta)[1]

            print(curr_score)
            print(move)
            # If this score is better (lower) than the score associated with the best move we found so far, update it
            if curr_score < min_score:
                min_score = curr_score
                best_move = move

            beta = min(beta, curr_score)
            if beta <= alpha:
                break

        return best_move, min_score

    # Eventual parameters board_copy, depth - 1, alpha, beta, player
    def minimax(self, game_state: GameState, player_number, maximizing_player: bool, depth, alpha, beta) -> Move:
        '''
        Minimax algorithm with alpha-beta pruning.
        @param game_state: A Sudoku game state, with board and moves
        @param player_number: A player number, either 1 or 2
        @param depth: (Remaining) depth of the minimax algorithm
        @param alpha: The alpha in alpha-beta pruning
        @param beta: The beta in alpha-beta pruning
        @return: The move that the current player should play and the associated score
        '''
        all_moves = self.get_all_moves(game_state)
        max_moves = game_state.initial_board.squares.count(SudokuBoard.empty)
        number_of_moves = len(game_state.moves)
        # print(number_of_moves, max_moves)
        # print(game_state)
        # print('all_moves', len(all_moves))

        if depth == 0 or not (len(all_moves) > 0) or number_of_moves >= max_moves:
            print(depth == 0, not len(all_moves) > 0, number_of_moves < max_moves)
            print('\r[MiniMax] Ending minimax..')
            return None, game_state.scores[player_number-1]

        if maximizing_player:
            print('\r[MiniMax] Maximizing player')
            best_move, score = self.max(game_state, all_moves, player_number, depth, alpha, beta)
        else:
            print('\r[MiniMax] Minimizing player')
            best_move, score = self.min(game_state, all_moves, player_number, depth, alpha, beta)

        return best_move, score

