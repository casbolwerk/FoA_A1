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
        # initiate a random valid move, so some move is always returned
        # this is needed in case our minimax does not finish at least one evaluation to ensure we do not hit a "no move selected"
        #    as this would instantly lose us the game
        all_moves = self.get_all_moves(game_state)
        proposal = random.choice(all_moves)
        self.propose_move(proposal)

        #introducing a null move to allow for initial call
        nullMove = Move(-1, -1, -1)
        #while True:
        #    time.sleep(0.2)
        #    self.propose_move(random.choice(all_moves))
        depth = 1
        meta = Metadata(nullMove, proposal, -math.inf)
        while True:
        #initiate a metadata to be sent with the original call, consisting of nullmove, the picked "fallback" move and
        #  a score of -inf to ensure any computed move is picked during computation to replace it
        #  Note: as we do not know if this move is an improvement over the random move, this essentially serves as another random move
        #         but it ensures once again that we do have a selected move, which now is evaluated and to be compared with others
            game_state.initial_board = game_state.board
            best_move, best_score, meta = self.alphabeta(game_state, meta, True, depth, -math.inf, math.inf)
            self.propose_move(best_move)

            depth = depth + 1

    def hasEmpty(self, board: SudokuBoard) -> bool:
        for i in range(board.N):
            for j in range(board.N):
                if board.get(i, j) is SudokuBoard.empty:
                    return True
        return False

    #TODO to improve the amount of data passed each time, exchange game_state with a combination of board and all_moves list
    # update all_moves and board before passing along a new instance for the next call
    def alphabeta(self, game_state: GameState, meta: Metadata, maximizing_player: bool, depth, alpha, beta) -> (Move, int, Metadata):
        nullMove = Move(-1, -1, -1)
        #get a list of all possible moves using the input gamestate
        all_moves = self.get_all_moves(game_state)
        #is this the final level to consider?
        if depth == 0 or len(all_moves) == 0:
            #print('stopping minmax')
            #check if the game didnt deadlock
            if len(all_moves) == 0 and self.hasEmpty(game_state.board):
                return nullMove, -math.inf, meta
            #TODO: heuristic function to evaluate current board (based on last move)
            return nullMove, self.evaluate_state(game_state, meta.last_move), meta
            return nullMove, diff_score(game_state.scores), meta
            #return None, 0
        depth_1_scores = self.check_random_move(game_state, all_moves)
        # if depth_1_scores.count(depth_1_scores[0]) == len(depth_1_scores) and depth_1_scores[0] == 0:
        #     #print('do random move')
        #     return random.choice(all_moves), 0
        # else:
        #     all_moves = [move for (move, depth_1_filter) in zip(all_moves, depth_1_scores) if depth_1_filter]
        # #not the final move, check if maximizing player
        if maximizing_player:
            #print('now maximizing')
            #start with -infty
            best_value = -math.inf
            best_move = random.choice(all_moves)
            for move in all_moves:
                #print('maximizing for move ', move, 'at depth', depth)
                #update new gamestate
                new_gs = deepcopy(game_state)
                new_gs.board.put(move.i, move.j, move.value)
                new_gs.moves.append(move)
                new_gs.taboo_moves = self.update_taboo_moves(new_gs)
                player_number = 1 if len(game_state.moves) % 2 == 0 else 2
                new_gs.scores[player_number-1] = new_gs.scores[player_number-1] + move_score(new_gs.board, move)
                meta.setLast(move)
                new_value = max(best_value, self.alphabeta(new_gs, meta, False, depth - 1, alpha, beta)[1])
                #print("MAX:  Move ", move.__str__(), " has value ", new_value, " at height ", depth)
                #print('NEW VALUE ', new_value)
                # update best move and global value to the new move as long as it is at least as good as the previous best
                if new_value > best_value:
                    #print("We found a better value with old: ", best_value, " and new: ", new_value)
                    #print('UPDATING MAX BEST MOVE', best_value, new_value)
                    best_value = new_value
                    best_move = move
                # update alpha if allowed to continue
                alpha = max(alpha, new_value)
                # compare whether the new found move is an improvement over the overall computed proposal
                # if new_value > meta.best_score:
                #     #print("Update proposal and metadata")
                #     #print("New proposal inserted", meta.best_move.__str__(), meta.best_score, " replaced with ", move.__str__(), new_value)
                #     meta.set(meta.last_move, move, new_value)
                #     # if it is, then submit it as the new proposal
                #     self.propose_move(move)

                # compare to beta to check for breakoff
                if beta <= alpha:
                    #print('BETA BREAK', beta, '<=', alpha)
                    break
            #after the loop, return the best move and its associated value
            return best_move, best_value, meta
        else:
            #print('now minimizing')
            # minimizing player start with infty
            best_value = math.inf
            best_move = random.choice(all_moves)
            for move in all_moves:
                #print('minimizing for move ', move, 'at depth', depth)
                #update new gamestate
                new_gs = deepcopy(game_state)
                new_gs.board.put(move.i, move.j, move.value)
                new_gs.moves.append(move)
                new_gs.taboo_moves = self.update_taboo_moves(new_gs)
                player_number = 1 if len(game_state.moves) % 2 == 0 else 2
                new_gs.scores[player_number-1] = new_gs.scores[player_number-1] + move_score(new_gs.board, move)
                meta.setLast(move)
                new_value = min(best_value, self.alphabeta(new_gs, meta, True, depth - 1, alpha, beta)[1])
                #print("MIN:   Move ", move.__str__(), " has value ", new_value, " at height ", depth)
                if new_value < best_value:
                    #print('UPDATING MIN BEST MOVE', best_value, new_value)
                    best_value = new_value
                    best_move = move
                #update beta if allowed to continue
                beta = min(beta, new_value)
                # compare the alpha to check for breakoff
                if beta <= alpha:
                    #print('ALPHA BREAK', beta, '<=', alpha)
                    break
            #after the loop, return the best move and its associated value
            return best_move, best_value, meta

    @staticmethod
    def evaluate_state(game_state: GameState, last_move: Move) -> int:
        p1_score = game_state.scores[0]
        p2_score = game_state.scores[1] # odd movecount/turns
        temp_score = game_state.scores

        difference = diff_score(game_state.scores) #how much p1 is ahead of p2 (negative implies behind)

        curr_player_number = 1 if len(game_state.moves) % 2 == 0 else 2
        possible_opp_gain = immediate_gain(game_state.board, last_move)

        # score_advantage = difference - possible_opp_gain if curr_player_number == 1 else difference + possible_opp_gain

        # if curr_player is 1 then player 2 scores the "Easily obtained" points, else player 1 scores them
        score_advantage = difference
        def hasEmpty(board: SudokuBoard) -> bool:
            for i in range(board.N):
                for j in range(board.N):
                    if board.get(i, j) is SudokuBoard.empty:
                        return True
            return False
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
        
        
        
        