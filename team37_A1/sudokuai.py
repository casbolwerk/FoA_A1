#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from copy import deepcopy

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team37_A1.heuristics import move_score, diff_score, immediate_gain, prepares_sections
from team37_A1.metadata import Metadata

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """
    def __init__(self):
        super().__init__()

    def check_square(self, game_state, i, j, value):
        """
        Check whether the value inputted by a move in position (i, j) violates the games ruleset.
        @param game_state: The game state on which to check the moves validity
        @param i: The row position of the move
        @param j: The column position of the move
        @param value: The value to be entered in the moves position (i, j)
        @return: Whether the value already occurs in the square in which the move occurs
        """
        rows = game_state.board.m
        columns = game_state.board.n
 
        # convert row and column to the correct square on the board               
        introw = math.ceil((i + 1) / rows)
        intcol = math.ceil((j + 1) / columns)
        
        for p in range(((introw - 1) * rows), (introw * rows)):
            for q in range(((intcol - 1) * columns), (intcol * columns)):
                if game_state.board.get(p, q) == value:
                    return False
        return True

    def check_column(self, game_state, N, j, value):
        """
        Check whether the value inputted by a move in column position j violates the games ruleset.
        @param game_state: The game state on which to check the moves validity
        @param N: The number of rows to check
        @param j: The column for which to check
        @param value: The value to be entered in the column
        @return: Whether the value already occurs in the column
        """
        for p in range(N):
            if game_state.board.get(p, j) == value:
                return False
        return True

    def check_row(self, game_state, N, i, value):
        """
        Check whether the value inputted by a move in row position i violates the games ruleset.
        @param game_state: The game state on which to check the moves validity
        @param N: The number of columns to check
        @param i: The row for which to check
        @param value: The value to be entered in the row
        @return: Whether the value already occurs in the row
        """
        for q in range(N):
            if game_state.board.get(i, q) == value:
                return False
        return True

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
        N = game_state.board.N
        # Return whether the move violates any of the games rules
        if not (self.check_column(game_state, N, j, value) == self.check_row(game_state, N, i, value) ==
                self.check_square(game_state, i, j, value) == True):
            return False
        else:
            return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j,
                                                                                     value) in game_state.taboo_moves

    def get_all_moves(self, game_state: GameState):
        """
        Gets all the possible moves from the current state of the game.
        @param game_state: The current state of the game
        @return: A list with all possible moves
        """
        N = game_state.board.N

        rows = game_state.board.m
        columns = game_state.board.n

        # Selects only those moves which do not violate the rules
        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if
                     self.possible_move(game_state, i, j, value, rows, columns)]

        return all_moves

    def update_taboo_moves(self, game_state:GameState):
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

    @staticmethod
    def check_random_move(game_state: GameState, all_moves: [Move]):
        """
        Compute the game state scores resulting from all first moves from the input game state.
        @param game_state: The game state to start computation on
        @param all_moves: The set of all possible moves to attempt
        @return: A list of scores that can be gained from all moves in the input all_moves
        """
        depth_1_scores = []
        for move in all_moves:
            new_gs = deepcopy(game_state)
            new_gs.board.put(move.i, move.j, move.value)
            depth_1_scores.append(move_score(new_gs.board, move))
        return depth_1_scores

    def compute_best_move(self, game_state: GameState) -> None:
        """
        Compute the best possible move to be made during the players turn based on the Minimax algorithm
            using Alpha-Beta pruning.
        @param game_state: The initial game state to calculate a move on.
        @return:
        """
        # Initiate a random valid move, so some move is always returned.
        # This is needed in case our minimax does not finish at least one evaluation to ensure we do not hit a "no move selected"
        #    as this would instantly lose us the game.
        all_moves = self.get_all_moves(game_state)
        proposal = random.choice(all_moves)
        # Propose the fallback move
        self.propose_move(proposal)

        # Introducing a null move to allow for initial call
        nullMove = Move(-1, -1, -1)

        # Set the initial starting depth
        depth = 1

        """
        Initiate a Metadata object to be sent with the original alphabeta() function call, consisting of:
        - last_move: a null move as initiated above
        - best_move: the fallback move
        - best_value: - infinity to ensure any computed move overwrites the fallback.
        """
        meta = Metadata(nullMove, proposal, -math.inf)

        """
        As the time per turn is undefined and we will be interrupted in a way that our last proposed move is used,
        we can incrementally increase the depth at which our alphabeta tree is evaluating game states.
        We do this through a never ending while loop which first computes the best move at some depth, proposes this move
        and then increments the depth by 1.
        """
        while depth < 3:
            print('CURRENT DEPTH', depth)
            best_move, best_score, meta = self.alphabeta(game_state, meta, True, depth, -math.inf, math.inf)
            print('new best move:', best_move, 'for score', best_score)
            self.propose_move(best_move)

            depth = depth + 1

    def hasEmpty(self, board: SudokuBoard) -> bool:
        """
        Check whether there is empty spaces left on the board.
        @param board: The board to check for empty spaces
        @return: Whether there is at least one empty space on the input board.
        """
        for i in range(board.N):
            for j in range(board.N):
                if board.get(i, j) is SudokuBoard.empty:
                    return True
        return False

    def alphabeta(self, game_state: GameState, meta: Metadata, maximizing_player: bool, depth, alpha, beta) -> (Move, int, Metadata):
        """
        Perform a minimax algorithm using Alpha-Beta pruning.
        @param game_state: The current game state to consider at the root node of the alphabeta() routine
        @param meta: The metadata attached to the current routine and turn computation
        @param maximizing_player: Whether the current routine call concerns the maximizing player
        @param depth: The maximum depth the routine is supposed to reach
        @param alpha: The current alpha value to be considered for pruning
        @param beta: The current beta value to be considered for pruning
        @return:
        """
        # Default nullMove for referencing (this ensures that any call with no move is able to be compared with moves it may encounter)
        nullMove = Move(-1, -1, -1)
        # Get a list of all possible moves using the input gamestate
        all_moves = self.get_all_moves(game_state)
        # Check whether we reached a leaf node or the maximum depth we intend to search on
        if depth == 0 or len(all_moves) == 0:
            print("Evaluation of move: " + "Row: " + str(meta.last_move.i) + " Col: " + str(
                meta.last_move.j) + " Value: " + str(meta.last_move.value) + " and evaluation score: " + str(
                self.evaluate_state(game_state, meta.last_move)))
            # Check if the game finished
            if len(all_moves) == 0:
                print('all_moves 0')
                if not self.hasEmpty(game_state.board):
                    # As we've reach a state we cannot move from any longer so we return the final score of the board
                    return nullMove, diff_score(game_state.scores), meta
                else:
                    print('invalid move')
                    # We cannot perform any more moves but the game is not finished, we've hit a deadlock
                    # We avoid this deadlock path by checking for nullMoves in choosing best moves
                    return nullMove, None, meta

            # Evaluate the leaf node based on the heuristics function "evaluate_state"
            return nullMove, self.evaluate_state(game_state, meta.last_move), meta

        # depth_1_scores = self.check_random_move(game_state, all_moves)
        # if depth_1_scores.count(depth_1_scores[0]) == len(depth_1_scores) and depth_1_scores[0] == 0:
        #     return random.choice(all_moves), 0, meta
        # else:
        #     all_moves = [move for (move, depth_1_filter) in zip(all_moves, depth_1_scores) if depth_1_filter]

        # Not a leaf node, compute the best option among the sub-trees according to the maximizing_player parameter
        if maximizing_player:
            # Start with -infty
            best_value = -math.inf
            # Pick a random move to ensure some move will be returned after computation
            best_move = random.choice(all_moves)

            # Compute the best sub-tree each created using one of the possible moves
            for move in all_moves:
                # Create a copy of the game_state (to avoid any backward passing problems)
                new_gs = deepcopy(game_state)
                # Update the copied game state with the information resulting from the executed move
                new_gs.board.put(move.i, move.j, move.value)
                new_gs.moves.append(move)
                new_gs.taboo_moves = self.update_taboo_moves(new_gs)
                # Update the scores in the game
                player_number = 1 if len(game_state.moves) % 2 == 0 else 2
                new_gs.scores[player_number-1] = new_gs.scores[player_number-1] + move_score(new_gs.board, move)
                # Update the metadata, note that meta.best_move and meta.best_value did not change (yet)
                meta.setLast(move)
                # Compute and compare the evaluation of further subtree's selecting the maximum of the highest found sub-tree and the current sub-tree
                curr_value = self.alphabeta(new_gs, meta, False, depth - 1, alpha, beta)[1]
                if curr_value is None:
                    print('invalid encountered')
                    if len(all_moves) == 1:
                        if maximizing_player:
                            print('maximizing unsolvable')
                            return nullMove, math.inf, meta
                        else:
                            print('minimizing unsolvable')
                            return nullMove, -math.inf, meta
                    continue
                new_value = max(best_value, curr_value)

                print(move, new_value)
                if new_value > best_value:
                    print("Alphabeta returns: " + "Score: " + str(curr_value) + " and compares that to prev best value " +
                          str(best_value) + " and True if maximizing: " + str(maximizing_player))
                    moves = [str(move) for move in new_gs.moves]
                    for new_move in moves:
                        print(new_move)
                    best_value = new_value
                    best_move = move

                alpha = max(alpha, new_value)

                if beta <= alpha:
                    print('maximizing break')
                    break

            # Return the best move found at the root node
            return best_move, best_value, meta
        else:
            # This is the minimizing players actions

            # Start with infty
            best_value = math.inf
            # Pick a random move to ensure some move will be returned after computation
            best_move = random.choice(all_moves)
            if len(game_state.moves) > 0:
                print('PREV MOVE IN GAME TREE', game_state.moves[-1])

            # Compute the best sub-tree each created using one of the possible moves
            for move in all_moves:
                # Create a copy of the game_state (to avoid any backward passing problems)
                new_gs = deepcopy(game_state)
                # Update the copied game state with the information resulting from the executed move
                new_gs.board.put(move.i, move.j, move.value)
                new_gs.moves.append(move)
                new_gs.taboo_moves = self.update_taboo_moves(new_gs)
                # Update the scores in the game
                player_number = 1 if len(game_state.moves) % 2 == 0 else 2
                new_gs.scores[player_number-1] = new_gs.scores[player_number-1] + move_score(new_gs.board, move)
                # Update the metadata, note that meta.best_move and meta.best_value did not change (yet)
                meta.setLast(move)
                # Compute and compare the evaluation of further subtree's selecting the minimum of the lowest found sub-tree and the current sub-tree
                curr_value = self.alphabeta(new_gs, meta, True, depth - 1, alpha, beta)[1]
                if curr_value is None:
                    print('invalid encountered')
                    if len(all_moves) == 1:
                        if maximizing_player:
                            print('maximizing unsolvable')
                            return nullMove, math.inf, meta
                        else:
                            print('minimizing unsolvable')
                            return nullMove, -math.inf, meta
                    continue
                new_value = min(best_value, curr_value)

                if new_value < best_value:
                    print("Alphabeta returns: " + "Score: " + str(curr_value) + " and compares that to prev best value " +
                          str(best_value) + " and True if maximizing: " + str(maximizing_player))
                    moves = [str(move) for move in new_gs.moves]
                    for new_move in moves:
                        print(new_move)
                    best_value = new_value
                    best_move = move

                beta = min(beta, new_value)

                if beta <= alpha:
                    print('minimizing break')
                    break

            # Return the best move found at the root node
            return best_move, best_value, meta

    def evaluate_state(self, game_state: GameState, last_move: Move) -> int:
        """
        Evaluates the current state of the game.
        @param game_state: The game state to evaluate
        @param last_move: The last move made in the sub-tree
        @return: An evaluation of the input game state
        """
        # Use the naive implementation (only the score difference of the resulting board state)
        naive = True

        difference = diff_score(game_state.scores) #how much p1 is ahead of p2 (negative implies behind)
        score_advantage = difference

        if not naive:
            # Check who's turn it is
            curr_player_number = 1 if len(game_state.moves) % 2 == 0 else 2
            # Compute whether there are points to be scored by the opponent in the next turn
            possible_opp_gain = immediate_gain(game_state.board, last_move)

            # Check whether the game has ended with the last turn
            if not hasEmpty(game_state.board):
                # Check whether the resulting score is winning
                winning = difference >= 0 if curr_player_number == 1 else difference < 0
                # Update the evaluation based on whether the player is winning
                if winning:
                    score_advantage = score_advantage + 10 # if curr_player_number == 1 else score_advantage - 100
            else:
                # Otherwise use a combination of the score difference and the possible gain by the opponent (which reduces the score)
                score_advantage = difference - possible_opp_gain if curr_player_number == 1 else difference + possible_opp_gain

        return score_advantage
        
        
        
        

