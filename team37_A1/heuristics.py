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


def diff_score(scores) -> int:
    return scores[0] - scores[1]
