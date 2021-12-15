#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from copy import deepcopy
import itertools

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team37_A1.heuristics import move_score, diff_score, prepares_sections, \
                                 single_possibility_sudoku_rule, all_possibilities, retrieve_board_status
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

    def possible_move(self, game_state, i, j, value):
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
                     self.possible_move(game_state, i, j, value)]

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
                if not self.possible_move(game_state, i, _j, value):
                    taboo_moves.append(taboo_move)
            for _i in range(N):
                taboo_move = Move(_i, j, value)
                if not self.possible_move(game_state, _i, j, value):
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
        curr_player = 1 if len(game_state.moves) % 2 == 0 else 2
        # Initiate a random valid move, so some move is always returned.
        # This is needed in case our minimax does not finish at least one evaluation to ensure we do not hit a "no move selected"
        #    as this would instantly lose us the game.
        all_moves = self.get_all_moves(game_state)
        proposal = random.choice(all_moves)
        # Propose the fallback move
        self.propose_move(proposal)

        # Introducing a null move to allow for initial call
        nullMove = Move(-1, -1, -1)

        """
        Initiate a Metadata object to be sent with the original alphabeta() function call, consisting of:
        - last_move: a null move as initiated above
        - best_move: the fallback move
        - best_value: - infinity to ensure any computed move overwrites the fallback.
        """
        meta = Metadata(nullMove, proposal, -math.inf)

        # Set the initial starting depth
        depth = 1
        """
        As the time per turn is undefined and we will be interrupted in a way that our last proposed move is used,
        we can incrementally increase the depth at which our alphabeta tree is evaluating game states.
        We do this through a never ending while loop which first computes the best move at some depth, proposes this move
        and then increments the depth by 1.
        """
        while True:
            # print('CURRENT DEPTH', depth)
            best_move, best_score, meta = self.alphabeta(game_state, meta, True, depth, -math.inf, math.inf, curr_player)
            # print('new best move', best_move, 'with a score of', best_score)
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

    def alphabeta(self, game_state: GameState, meta: Metadata, maximizing_player: bool, depth, alpha, beta, curr_player) -> (Move, int, Metadata):
        """
        Perform a minimax algorithm using Alpha-Beta pruning.
        @param game_state: The current game state to consider at the root node of the alphabeta() routine
        @param meta: The metadata attached to the current routine and turn computation
        @param maximizing_player: Whether the current routine call concerns the maximizing player
        @param depth: The maximum depth the routine is supposed to reach
        @param alpha: The current alpha value to be considered for pruning
        @param beta: The current beta value to be considered for pruning
        @param curr_player: Const for the player that is being played by the team37_A1 alphabeta
        @return: (Move, int, Metadata)
            - Move: the best move found
            - int: the evaluation of the best move
            - Metadata: a metadata packet from the resulting computation
        """
        # Default nullMove for referencing (this ensures that any call with no move is able to be compared with moves it may encounter)
        nullMove = Move(-1, -1, -1)

        # Get a list of moves that are certainly right
        all_moves = single_possibility_sudoku_rule(game_state)
        # If there are less than 3 moves of which we can be sure that they would not be rejected by the Oracle
        if len(all_moves) < 3:
            # EARLY GAME (or late game but then all moves are considered anyway by the below code)
            # Retrieve the moves for the x cells where we can be most certain that the proposed values are right
            all_options = all_possibilities(game_state)
            all_moves = []
            # TODO: add a ratio to limit all_options
            # Look at the first x cells (ratio of NxM)
            count = 0
            poss_threshold = game_state.board.N**2/2
            if not len(all_options) > poss_threshold:
                poss_threshold = len(all_options)
            # print('\n\nTHRESHOLD', poss_threshold)
            for key in dict(itertools.islice(all_options.items(), poss_threshold)):
                # if count < x:
                #     count += 1
                for value in all_options[key]:
                    all_moves.append(Move(key[0], key[1], value))

        # Filter out any rule-breaking or taboo moves
        all_moves = [move for move in all_moves if self.possible_move(game_state, move.i, move.j, move.value)]

        # Check whether we reached a leaf node or the maximum depth we intend to search on
        if depth == 0 or len(all_moves) == 0:
            # print("Evaluation of move: " + "Row: " + str(meta.last_move.i) + " Col: " + str(
            #     meta.last_move.j) + " Value: " + str(meta.last_move.value) + " and evaluation score: " + str(
            #     self.evaluate_state(game_state, meta.last_move, curr_player)))
            # Check if the game finished
            if len(all_moves) == 0:
                if not self.hasEmpty(game_state.board):
                    # The game has finished so we return the final score of the board
                    return nullMove, diff_score(game_state.scores), meta
                else:
                    # We cannot perform any more moves but the game is not finished, we've hit a deadlock
                    # We avoid this deadlock path by checking for nullMoves in choosing best moves
                    return nullMove, None, meta

            # Evaluate the leaf node based on the heuristics function "evaluate_state"
            return nullMove, self.evaluate_state(game_state, meta.last_move, curr_player), meta

        # Not a leaf node, compute the best option among the sub-trees according to the maximizing_player parameter
        if maximizing_player:
            # if len(game_state.moves) > 0:
            #     print('PREV MOVE IN GAME TREE', game_state.moves[-1])
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
                curr_value = self.alphabeta(new_gs, meta, False, depth - 1, alpha, beta, curr_player)[1]
                # Check whether a guaranteed unsolvable board was encountered
                if curr_value is None:
                    # Check whether it is the only option in the subtree
                    if len(all_moves) == 1:
                        # If it is the only option, then ensure that the root of the subtree never picks this subtree
                        if maximizing_player:
                            return nullMove, math.inf, meta
                        else:
                            return nullMove, -math.inf, meta
                    # Skip this move as it should never be picked
                    continue
                new_value = max(best_value, curr_value)

                if new_value > best_value:
                    # print("Alphabeta returns: " + "Score: " + str(curr_value) + " and compares that to prev best value " +
                    #       str(best_value) + " and True if maximizing: " + str(maximizing_player))
                    # moves = [str(move) for move in new_gs.moves]
                    # if len(moves) > 3:
                    #     for new_move in moves[:-3]:
                    #         print(new_move)
                    best_value = new_value
                    best_move = move

                alpha = max(alpha, new_value)

                if beta <= alpha:
                    break

            # Return the best move found at the root node
            return best_move, best_value, meta
        else:
            # if len(game_state.moves) > 0:
            #     print('PREV MOVE IN GAME TREE', game_state.moves[-1])
            # This is the minimizing players actions
            # Start with infty
            best_value = math.inf
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

                # Compute and compare the evaluation of further subtree's selecting the minimum of the lowest found sub-tree and the current sub-tree
                curr_value = self.alphabeta(new_gs, meta, True, depth - 1, alpha, beta, curr_player)[1]
                # Check whether a guaranteed unsolvable board was encountered
                if curr_value is None:
                    # Check whether it is the only option in the subtree
                    if len(all_moves) == 1:
                        # If it is the only option, then ensure that the root of the subtree never picks this subtree
                        if maximizing_player:
                            return nullMove, math.inf, meta
                        else:
                            return nullMove, -math.inf, meta
                    # Skip this move as it should never be picked
                    continue
                new_value = min(best_value, curr_value)

                if new_value < best_value:
                    # print("Alphabeta returns: " + "Score: " + str(curr_value) + " and compares that to prev best value " +
                    #       str(best_value) + " and True if maximizing: " + str(maximizing_player))
                    # moves = [str(move) for move in new_gs.moves]
                    # if len(moves) > 3:
                    #     for new_move in moves[:-3]:
                    #         print(new_move)
                    best_value = new_value
                    best_move = move

                beta = min(beta, new_value)

                if beta <= alpha:
                    break

            # Return the best move found at the root node
            return best_move, best_value, meta

    def evaluate_state(self, game_state: GameState, last_move: Move, curr_player) -> int:
        """
        Evaluates the current state of the game.
        @param game_state: The game state to evaluate
        @param last_move: The last move made in the sub-tree
        @return: An evaluation of the input game state
        """
        # Use the naive implementation (only the score difference of the resulting board state)
        # A2 deadline: set naive to False
        naive = True

        difference = diff_score(game_state.scores) #how much p1 is ahead of p2 (negative implies behind)
        difference = difference if curr_player == 1 else difference * -1
        score_advantage = difference

        if not naive:
            # Start a variable for the current board state:
            board_score = 0
            # Compute how many points were obtained using the last_move (Add higher priority to scored points by multiplying by 10)
            score_obtained = move_score(game_state.board, last_move) * 10
            # Check who's turn it is
            curr_player_number = 1 if len(game_state.moves) % 2 == 0 else 2
            # Compute the number of empty cells left in the board as well as the amount of points the opponent can immediately score (potentially)
            empties, possible_opp_gain = retrieve_board_status(game_state.board, last_move)
            # Add higher priority to directly available points (on the same tier as directly scored points)
            possible_opp_gain = possible_opp_gain * 10

            # Score the board state +1 for each region that is left with an even number of empty cells and -1 for each region with an odd number of remaining empty cells
            for region_empties in empties:
                if region_empties % 2 == 0:
                    board_score = board_score + 1
                else:
                    board_score = board_score - 1

            # Update the board_score using the gained points, the possible gain from the opponent afterwards, and the difference in scores after the move is made
            board_score = board_score + score_obtained - possible_opp_gain + difference

            return board_score

        return score_advantage