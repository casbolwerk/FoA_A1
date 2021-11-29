import math


from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove


def completes_square(board, i, j):
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
    for p in range(N):
        if board.get(p, j) is SudokuBoard.empty:
            return False
    return True


def completes_row(board, N, i):
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
    #print('SCORE ADDED', scores[move_score])

    return scores[move_score]

    #return the number of empty squares in the row including the most recent move
def leaves_row(board, N, i) -> int:
    count = 0
    for q in range(N):
        if board.get(i, q) is SudokuBoard.empty:
            count = count + 1
    return count

    #return the number of empty squares in the column including the most recent move
def leaves_col(board, N, j) -> int:
    count = 0
    for p in range(N):
        if board.get(p, j) is SudokuBoard.empty:
            count = count + 1
    return count

    #return the number of empty squares in the region including the most recent move
def leaves_square(board, i, j) -> int:
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
    Calculate the score that can immediately be obtained by a move in the next turn
    @param board:
    @param move:
    @return:
    """
    i, j = move.i, move.j
    N = board.N
    leaves = [leaves_square(board, i, j) == 1, leaves_col(board, N, j) == 1, leaves_row(board, N, i) == 1]

    move_score = leaves.count(True)
    scores = [0, 1, 3, 7]
    # print('SCORE ADDED', scores[move_score])

    return scores[move_score]

def prepares_sections(board: SudokuBoard, move: Move):
    i, j = move.i, move.j
    N = board.N
    prepared = [leaves_square(board, i, j) == 2, leaves_col(board, N, j) == 2, leaves_row(board, N, i) == 2]
    return prepared.count(True)

def is_closest(board: SudokuBoard, move: Move):
    i, j = move.i, move.j
    fullest_square = 0
    fullest_col = 0
    fullest_row = 0
    for i in range(board.N):
        row = leaves_row(board, board.N, i)
        if row >= 3:
            fullest_row = max(fullest_row, row)
        for j in range(board.N):
            col = leaves_col(board, board.N, j)
            if col >= 3:
                fullest_col = max(fullest_col, col)
            square = leaves_square(board, i, j)
            if square >= 3:
                fullest_square = max(square, fullest_square)
    # fullest_square = max([leaves_square(board, i, j) for i in range(board.N) and j in range(board.N) if (leaves_square(board, i, j) > 2)])
    # fullest_col = max([leaves_col(board, board.N, j) for j in range(board.N) if leaves_col(board, board.N, j) > 2])
    # fullest_row = max([leaves_row(board, board.N, i) for i in range(board.N) if leaves_row(board, board.N, i) > 2])

    return [leaves_square(board, move.i, move.j) == fullest_square, leaves_col(board, board.N, move.j) == fullest_col, leaves_row(board, board.N, move.i) == fullest_row]

def diff_score(scores) -> int:
    return scores[0] - scores[1]
