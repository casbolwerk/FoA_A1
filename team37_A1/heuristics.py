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

#TODO: merge with single_possibility_sudoku_rule branch
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
    leaves = [empties[0] == 1, empties[1] == 1, empties[2] == 1]

    move_scores = leaves.count(True)
    scores = [0, 1, 3, 7]

    return empties, scores[move_scores]

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
