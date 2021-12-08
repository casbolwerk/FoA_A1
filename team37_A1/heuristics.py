import math

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove


def completes_square(board, i, j):
    """
    Calculate whether the move to position (i, j) on the board completes its square
    @param board: The board, including the filled entry in (i, j)
    @param i: The row position of the to check entry
    @param j: The column position of the to check entry
    @return: Whether the square the entry is in is now completed
    """
    rows = board.m
    columns = board.n
    introw = math.ceil((i + 1) / rows)
    intcol = math.ceil((j + 1) / columns)
    for p in range(((introw  - 1) * rows), (introw  * rows)):
        for q in range(((intcol - 1) * columns), (intcol * columns)):
            if board.get(p, q) is SudokuBoard.empty:
                return False
    return True


def completes_col(board, N, j):
    """
    Calculate whether the move to position (i, j) on the board completes its column
    @param board: The board, including the filled entry in (i, j)
    @param i: The row position of the to check entry
    @param j: The column position of the to check entry
    @return: Whether the column the entry is in is now completed
    """
    for p in range(N):
        if board.get(p, j) is SudokuBoard.empty:
            return False
    return True


def completes_row(board, N, i):
    """
    Calculate whether the move to position (i, j) on the board completes its row
    @param board: The board, including the filled entry in (i, j)
    @param i: The row position of the to check entry
    @param j: The column position of the to check entry
    @return: Whether the row the entry is in is now completed
    """
    for q in range(N):
        if board.get(i, q) is SudokuBoard.empty:
            return False
    return True


def move_score(board: SudokuBoard, move: Move):
    '''
    Calculate the score that a move would give to the player
    @param board: the current board
    @param move: the latest move
    @return: the score that a move gives
    '''
    i, j = move.i, move.j
    N = board.N
    completes = [completes_square(board, i, j), completes_col(board, N, j), completes_row(board, N, i)]

    move_score = completes.count(True)
    scores = [0,1,3,7]

    return scores[move_score]


def leaves_row(board, N, i) -> int:
    """
    Compute the number of empty squares in the row i.
    @param board: The current board
    @param N: The number of column options to check
    @param i: The row in which to check
    @return: The number of empty squares in row i
    """
    count = 0
    for q in range(N):
        if board.get(i, q) is SudokuBoard.empty:
            count = count + 1
    return count


    #return the number of empty squares in the column including the most recent move
def leaves_col(board, N, j) -> int:
    """
    Compute the number of empty squares in the column j.
    @param board: The current board
    @param N: The number of row options to check
    @param j: The column in which to check
    @return: The number of empty squares in the column j
    """
    count = 0
    for p in range(N):
        if board.get(p, j) is SudokuBoard.empty:
            count = count + 1
    return count


    #return the number of empty squares in the region including the most recent move
def leaves_square(board, i, j) -> int:
    """
    Compute the number of empty squares in the region containing entry (i, j).
    @param board: The current board
    @param i: The row position to check for
    @param j: The column position to check for
    @return: The number of empty squares in the section in which entry (i, j) is located
    """
    count = 0
    rows = board.m
    columns = board.n
    introw = math.ceil((i + 1) / rows)
    intcol = math.ceil((j + 1) / columns)
    for p in range(((introw - 1) * rows), (introw * rows)):
        for q in range(((intcol - 1) * columns), (intcol * columns)):
            if board.get(p, q) is SudokuBoard.empty:
                count = count + 1
    return count


def immediate_gain(board: SudokuBoard, move: Move) -> int:
    """
    Calculate the score that can immediately be obtained by a move in the next turn.
    @param board: The current board
    @param move: The move to be performed
    @return: The amount of points gained as a result from the move on the provided board
    """
    i, j = move.i, move.j
    N = board.N
    leaves = [leaves_square(board, i, j) == 1, leaves_col(board, N, j) == 1, leaves_row(board, N, i) == 1]

    move_score = leaves.count(True)
    scores = [0, 1, 3, 7]

    return scores[move_score]


def prepares_sections(board: SudokuBoard, move: Move):
    """
    Check whether the provided move leaves a section on the board 2 turns from complete.
    @param board: The current board
    @param move: The move to check for
    @return: How many sections the move leaves with 2 turns from completion
    """
    i, j = move.i, move.j
    N = board.N
    prepared = [leaves_square(board, i, j) == 2, leaves_col(board, N, j) == 2, leaves_row(board, N, i) == 2]
    return prepared.count(True)


def diff_score(scores) -> int:
    """
    Compute the difference in score between player 1 and player 2.
    @param scores: The list of scores (size = 2)
    @return: The difference between the scores in the input list
    """
    return scores[0] - scores[1]


def single_possibility_sudoku_rule(game_state):
    """
    Implements the single possibility sudoku rule as stated on https://www.sudokudragon.com/sudokustrategy.htm .
    More specifically, finds a subset of legal moves that are the only moves that can be proposed for a certain cell
    and will therefore not be rejected.
    @param game_state: The current state of the game
    @return: List with moves that are the only options for the cells of the moves
    """

    N = game_state.board.N
    rows = game_state.board.m
    columns = game_state.board.n

    # Create a list with moves that are certainly right
    all_moves = []
    for i in range(N):
        for j in range(N):
            # If there is no value present in the cell already
            if game_state.board.get(i, j) == SudokuBoard.empty:
                values = possible_moves(game_state, N, i, j, rows, columns)
                if len(values) == 1:
                    all_moves.append(Move(i, j, values.iterator().next()))

    return all_moves


def all_possibilities(game_state):
    """
    Finds all possibilities for every square and sorts a dictionary with squares and number of possible values
    @param game_state: The current state of the game
    @return: Dictionary with empty squares and the amount of possible moves in those squares
    """

    N = game_state.board.N
    rows = game_state.board.m
    columns = game_state.board.n

    possibilities = {}

    for i in range(N):
        for j in range(N):
            # If there is no value present in the cell already
            if game_state.board.get(i, j) == SudokuBoard.empty:
                values = possible_moves(game_state, N, i, j, rows, columns)
                num_values = len(values)
                # Add the number of possible values to a dict with the corresponding square
                possibilities[(i, j)] = num_values

    # Sort the possibilities by the number of possible values, lower is better
    possibilities = {square: num_values for square, num_values in
                     sorted(possibilities.items(), key=lambda square_values: square_values[1])}

    return possibilities


def possible_moves(game_state, N, i, j, rows, columns) -> int:
    """
    For the given cell, checks if there is just one possible value that this cell can take and, in that case, returns
    this value. If there is not just a single possible value, the function returns 0.
    @param game_state: The current state of the game
    @param N:
    @param i:
    @param j:
    @param value:
    @param rows:
    @param columns:
    @return:
    """
    # Retrieve the sets of values that can be filled in in every region
    block = check_possible_values_block(game_state, N, i, j, rows, columns)
    row = check_possible_values_row(game_state, N, i, j, rows, columns)
    column = check_possible_values_column(game_state, N, i, j, rows, columns)

    # Take their intersection
    possible_values = block.intersection(row, column)

    # If there is only a single possible value return this value
    return possible_values


def check_possible_values_block(game_state, N, i, j, rows, columns) -> set:
    """
    Checks which values still need to be filled in in the block of the given cell.
    @param game_state: The current state of the game
    @param N: N
    @param i: Row of the given cell
    @param j: Column of the given cell
    @return: Set of values still to be filled in in the block
    """
    lst = list(range(1, N+1))
    possible_values = set(lst)

    # Convert row and column to the correct square on the board
    introw = math.ceil((i + 1) / rows)
    intcol = math.ceil((j + 1) / columns)

    # Find the values already present in the block
    present_values = set([])
    for p in range(((introw - 1) * rows), (introw * rows)):
        for q in range(((intcol - 1) * columns), (intcol * columns)):
            if game_state.board.get(p, q) != SudokuBoard.empty:
                present_values.add(game_state.board.get(p, q))

    # Return those values that are yet to be filled in in the block
    return possible_values.difference(present_values)


def check_possible_values_row(game_state, N, i, j, rows, columns) -> set:
    """
    Checks which values still need to be filled in in the row of the given cell.
    @param game_state: The current state of the game
    @param N: N
    @param i: Row of the given cell
    @param j: Column of the given cell
    @return: Set of values still to be filled in in the block
    """
    lst = list(range(1, N+1))
    possible_values = set(lst)

    # Find the values already present in the row
    present_values = set([])
    for q in range(N):
        if game_state.board.get(i, q) != SudokuBoard.empty:
            present_values.add(game_state.board.get(i, q))

    # Return those values that are yet to be filled in in the block
    return possible_values.difference(present_values)


def check_possible_values_column(game_state, N, i, j, rows, columns) -> set:
    """
    Checks which values still need to be filled in in the column of the given cell.
    @param game_state: The current state of the game
    @param N: N
    @param i: Row of the given cell
    @param j: Column of the given cell
    @return: Set of values still to be filled in in the block
    """
    lst = list(range(1, N+1))
    possible_values = set(lst)

    # Find the values already present in the row
    present_values = set([])
    for p in range(N):
        if game_state.board.get(p, j) != SudokuBoard.empty:
            present_values.add(game_state.board.get(p, j))

    # Return those values that are yet to be filled in in the block
    return possible_values.difference(present_values)


if __name__ == '__main__':
    from competitive_sudoku.sudoku import load_sudoku_from_text
    import copy
    from pathlib import Path
    board_text = Path('boards/easy-3x3.txt').read_text()
    board = load_sudoku_from_text(board_text)
    game_state = GameState(board, copy.deepcopy(board), [], [], [0, 0])
    all_possibilities(game_state)