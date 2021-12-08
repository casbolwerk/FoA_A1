import math

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove

def solvable_column(board: SudokuBoard, j: int):
    # for each empty entry in the column, check that at least one of the remaining (required) numbers still fits
    # the total entries required
    total = [i for i in range(board.N)]
    # the filled in entries
    filled = []
    # get the already filled numbers
    for p in range(N):
        if not board.get(p, j) is SudokuBoard.empty:
            filled.append(board.get(p, j))
    # for each empty entry, check if one number in total-filled doesnt break rules
    required = [i for i in total if i not in filled]
    # loop over the empty squares and check if there's at least one number in required that is not in the crossing row or square
    for p in range(N):
        if board.get(p, j) is SudokuBoard.empty:
            # position (p, j)
            # check if the row and square allow one of the values
            square_numbers = []
            introw = math.ceil((p + 1) / rows)
            intcol = math.ceil((j + 1) / columns)
            for k in range(((introw - 1) * rows), (introw * rows)):
                for l in range(((intcol - 1) * columns), (intcol * columns)):
                    if not board.get(k, l) is SudokuBoard.empty:
                        square_numbers.append(board.get(k, l))
            row_numbers = []
            for k in range(N):
                if not board.get(p, k) is SudokuBoard.empty:
                    row_numbers.append(board.get(p, k))
            remainder = [i for i in required if i not in row_numbers and i not in square_numbers]
            if len(remainder) == 0:
                return False
    # the input move doesnt lead to a directly unsolvable state
    return True

def solvable_row(board: SudokuBoard, i: int):
    return False

def solvable_square(board: SudokuBoard, i: int, j: int):
    return False

def remains_solvable(move: Move):
    return False