#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from copy import deepcopy


from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team37_A1.heuristics import move_score, diff_score, immediate_gain, prepares_sections, is_closest
from team37_A1.metadata import Metadata


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

    @staticmethod
    def check_random_move(game_state: GameState, all_moves: [Move]):
        #print('IN RANDOM MOVE')
        depth_1_scores = []
        for move in all_moves:
            new_gs = deepcopy(game_state)
            new_gs.board.put(move.i, move.j, move.value)
            depth_1_scores.append(move_score(new_gs.board, move))
        #print('depth_1_scores', depth_1_scores)
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
        while True:
            #game_state.initial_board = game_state.board TODO: is this needed for anything?
            best_move, best_score, meta = self.alphabeta(game_state, meta, True, depth, -math.inf, math.inf)
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

    # TODO: Implement an additional tracker which lets us store and potentially use a deadlock state,
    #           to adjust which player is taking the final turn of the game (and getting a default 7 points)
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
            # Check if the game finished
            if len(all_moves) == 0:
                if not self.hasEmpty(game_state.board):
                    # As we've reach a state we cannot move from any longer so we return the final score of the board
                    return nullMove, diff_score(game_state.scores), meta
                else:
                    # We cannot perform any more moves but the game is not finished, we've hit a deadlock
                    # We avoid this deadlock path by returning -math.inf as the evaluation
                    return nullMove, -math.inf, meta

            # Evaluate the leaf node based on the heuristics function "evaluate_state"
            return nullMove, self.evaluate_state(game_state, meta.last_move), meta
            #Alternative evaluation method: only consider the game score of the resulting board
            #return nullMove, diff_score(game_state.scores), meta

        #TODO: is this computation still worth using or do we abandon it?
        #depth_1_scores = self.check_random_move(game_state, all_moves)
        # if depth_1_scores.count(depth_1_scores[0]) == len(depth_1_scores) and depth_1_scores[0] == 0:
        #     #print('do random move')
        #     return random.choice(all_moves), 0
        # else:
        #     all_moves = [move for (move, depth_1_filter) in zip(all_moves, depth_1_scores) if depth_1_filter]
        #TODO: end todo

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
                new_value = max(best_value, self.alphabeta(new_gs, meta, False, depth - 1, alpha, beta)[1])

                # Update best move and global value to the new move as long as it is at least as good as the previous best
                if new_value >= best_value:
                    best_value = new_value
                    best_move = move

                # Compare the alpha and beta and break off further sub-tree computation if the alphabeta pruning requirement is met
                if beta <= alpha:
                    break

                # Update the alpha value
                alpha = max(alpha, new_value)

                # TODO: check whether this works even at depths lower than the root call depth (likely not)
                # """
                # Compare whether the new found move is an improvement over the overall computed proposal.
                # This can be done as we are exploring sub-trees at the same or a deeper depth than what is stored initially.
                # As we are in a maximizing step, if the evaluated value of such sub-tree is higher than what is stored,
                # We are guaranteed to pick a sub-tree at least as good as the current, thus we can update the proposed move
                # ahead of time, which will last until time runs out or another improvement is found.
                # @note: we use '>' over '>=' as there is more certainty in the results of sub-trees at a higher depth
                #         which means that an equal evaluation simply introduces additional risk.
                # """
                # if new_value > meta.best_score:
                #     # Update the metadata being passed along and propose the found move
                #     meta.set(meta.last_move, move, new_value)
                #     self.propose_move(move)

            # Return the best move found at the root node
            return best_move, best_value, meta
        else:
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
                new_value = min(best_value, self.alphabeta(new_gs, meta, True, depth - 1, alpha, beta)[1])

                # Update best move and global value to the new move as long as it is at least as good as the previous best
                if new_value < best_value:
                    best_value = new_value
                    best_move = move

                # compare the alpha to check for breakoff
                if beta <= alpha:
                    #print('ALPHA BREAK', beta, '<=', alpha)
                    break

                # Update the beta value
                beta = min(beta, new_value)
            # Return the best move found at the root node
            return best_move, best_value, meta

    @staticmethod
    def evaluate_state(game_state: GameState, last_move: Move) -> int:
        def hasEmpty(board: SudokuBoard) -> bool:
            for i in range(board.N):
                for j in range(board.N):
                    if board.get(i, j) is SudokuBoard.empty:
                        return True
            return False

        # def get_all_moves(game_state: GameState):
        #     N = game_state.board.N
        #
        #     rows = game_state.board.m
        #     columns = game_state.board.n
        #
        #     all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N + 1) if
        #                  self.possible_move(game_state, i, j, value, rows, columns)]
        #
        #     return all_moves
        #
        # # # check if the game didnt deadlock
        # if len(get_all_moves(game_state)) == 0 and hasEmpty(game_state.board):
        #     # we reached a deadlocked state which means that some move in the chain until this point causes the deadlock
        #     # TODO: somehow make the deadlocked turn have a better value so it is more likely to be picked such that the pace is reset
        #     #return nullMove, -math.inf, meta
        #     # if the pace determines loss, then pick this route
        #     #
        #     return 1

        p1_score = game_state.scores[0]
        p2_score = game_state.scores[1] # odd movecount/turns
        temp_score = game_state.scores

        difference = diff_score(game_state.scores) #how much p1 is ahead of p2 (negative implies behind)

        curr_player_number = 1 if len(game_state.moves) % 2 == 0 else 2
        possible_opp_gain = immediate_gain(game_state.board, last_move)

        # score_advantage = difference - possible_opp_gain if curr_player_number == 1 else difference + possible_opp_gain

        # if curr_player is 1 then player 2 scores the "Easily obtained" points, else player 1 scores them
        score_advantage = difference

        if not hasEmpty(game_state.board):
            #the game has ended with the last turn
            #check whether the resulting score is winning
            winning = difference >= 0 if curr_player_number == 1 else difference < 0
            if winning:
                score_advantage = score_advantage + 10 # if curr_player_number == 1 else score_advantage - 100
        else:
            score_advantage = difference - possible_opp_gain if curr_player_number == 1 else difference + possible_opp_gain
        # this counts if the move puts in the second to last value in a row, column or region
        # implying the opponent can immediately score it at least one of these (so the score advantage will be reduced by at least as many points as can now be scored)
        #score_advantage = 2*move_score(game_state.board, last_move) - possible_opp_gain + difference
        #score_advantage = 10 * (difference - possible_opp_gain)
        #print("Opponent can score: ", possible_opp_gain, " - the current score difference: ", difference, " - considering player number: ", curr_player_number)
        #score_advantage = 100 * (difference - possible_opp_gain) #if curr_player_number == 2 else 100 * (difference - possible_opp_gain)
        #print("So we get a score advantage of: ", score_advantage)
        # # value a move more if it prepares a section to N-2 completion
        # if prepares_sections(game_state.board, last_move) > 0:
        #      score_advantage = score_advantage + 20
        #
        # # value a move more if it brings any of the sections (col, row, region) closer to N-2 prepared
        # # prioritize filling up the most filled, non-prepared section as much as possible
        # fullest_count = is_closest(game_state.board, last_move)
        # score_advantage = fullest_count.count(True) * 5 #valued at 0, 5, 10, 15

        #return score_advantage
        #NAIVE:
        return score_advantage
        
        
        
        