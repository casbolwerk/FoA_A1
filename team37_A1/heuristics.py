import math

from copy import deepcopy

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
    @param N: The number of entries on a single column
    @param board: The board, including the filled entry in (i, j)
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
    @param N: The number of entries on a single row
    @param board: The board, including the filled entry in (i, j)
    @param i: The row position of the to check entry
    @return: Whether the row the entry is in is now completed
    """
    for q in range(N):
        if board.get(i, q) is SudokuBoard.empty:
            return False
    return True

def move_score(board: SudokuBoard, move: Move):
    """
    Calculate the score that a move would give to the player
    @param board: the current board
    @param move: the latest move
    @return: the score that a move gives
    """
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

def retrieve_board_status(board: SudokuBoard, move: Move):
    """
    Count the empty slots in the regions of the input move and check how many immediate points can be gained from the board.
    @param board:  The current board
    @param move: The move that was performed
    @return:
        - A list containing how many empty cells there are in [square, col, row]
        - The number of points that can immediately be scored on the remaining board
    """
    i, j = move.i, move.j
    N = board.N
    empties = [leaves_square(board, i, j), leaves_col(board, N, j), leaves_row(board, N, i)]

    scores = [0, 1, 3, 7]
    obtainable_points = 0

    if empties[0] == 1:
        # check the remaining empty in the same square
        # check what filling in the last empty would do i.e. count the empties of that row, square and col
        rows = board.m
        columns = board.n
        introw = math.ceil((i + 1) / rows)
        intcol = math.ceil((j + 1) / columns)
        for p in range(((introw - 1) * rows), (introw * rows)):
            for q in range(((intcol - 1) * columns), (intcol * columns)):
                if board.get(p, q) is SudokuBoard.empty:
                    temp_board = deepcopy(board)
                    temp_board.put(p, q, 1)
                    square_completes = [completes_square(temp_board, p, q), completes_col(temp_board, N, q), completes_row(temp_board, N, p)]
                    obtainable_points = max(obtainable_points, scores[square_completes.count(True)])

    if empties[1] == 1:
        # check the remaining empty in the same column
        # check what filling in the last empty would do i.e. count the empties of that row, square and col
        for p in range(N):
            if board.get(p, j) is SudokuBoard.empty:
                temp_board = deepcopy(board)
                temp_board.put(p, j, 1)
                col_completes = [completes_square(temp_board, p, j), completes_col(temp_board, N, j), completes_row(temp_board, N, p)]
                obtainable_points = max(obtainable_points, scores[col_completes.count(True)])

    if empties[2] == 1:
        # check the remaining empty on the same row
        # check what filling in the last empty would do i.e. count the empties of that row, square and col
        for q in range(N):
            if board.get(i, q) is SudokuBoard.empty:
                temp_board = deepcopy(board)
                temp_board.put(i, q, 1)
                row_completes = [completes_square(temp_board, i, q), completes_col(temp_board, N, q), completes_row(temp_board, N, i)]
                obtainable_points = max(obtainable_points, scores[row_completes.count(True)])

    return empties, obtainable_points

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
                    all_moves.append(Move(i, j, values.pop()))

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
                # Add the possible values to a dict with the corresponding cell
                possibilities[(i, j)] = values

    # Sort the possibilities by the number of possible values, lower is better
    possibilities = {cell: values for cell, values in
                     sorted(possibilities.items(), key=lambda cell_values: len(cell_values[1]))}

    return possibilities

def possible_moves(game_state, N, i, j, rows, columns) -> int:
    """
    For the given cell, checks if there is just one possible value that this cell can take and, in that case, returns
    this value. If there is not just a single possible value, the function returns 0.
    @param game_state: The current state of the game
    @param N: The total number of options available in any region
    @param i: The row position
    @param j: The column position
    @param rows: The number of rows per region
    @param columns: The number of columns per region
    @return: The number of possible values for some row and column position
    """
    # Retrieve the sets of values that can be filled in in every region
    block = check_possible_values_block(game_state, N, i, j, rows, columns)
    row = check_possible_values_row(game_state, N, i, j)
    column = check_possible_values_column(game_state, N, i, j)

    # Take their intersection
    possible_values = block.intersection(row, column)

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
    for s in range(((introw - 1) * rows), (introw * rows)):
        for t in range(((intcol - 1) * columns), (intcol * columns)):
            if game_state.board.get(s, t) != SudokuBoard.empty:
                present_values.add(game_state.board.get(s, t))

    # Return those values that are yet to be filled in in the block
    return possible_values.difference(present_values)


def check_possible_values_row(game_state, N, i, j) -> set:
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
    for p in range(N):
        if game_state.board.get(i, p) != SudokuBoard.empty:
            present_values.add(game_state.board.get(i, p))

    # Return those values that are yet to be filled in in the block
    return possible_values.difference(present_values)


def check_possible_values_column(game_state, N, i, j) -> set:
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
    for q in range(N):
        if game_state.board.get(q, j) != SudokuBoard.empty:
            present_values.add(game_state.board.get(q, j))

    # Return those values that are yet to be filled in in the block
    return possible_values.difference(present_values)

def compute_total_number_empty_cells(game_state):
    """
    Calculates the total number of empty cells on the board.
    @param game_state: The current state of the game
    """
    count = 0
    for m in range(game_state.board.N):
        for n in range(game_state.board.N):
            if game_state.board.get(m, n) == SudokuBoard.empty:
                count += 1

    return count

