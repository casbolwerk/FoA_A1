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

def check_square_board(board: SudokuBoard, i, j, value):
    """
    Check whether the value inputted by a move in position (i, j) violates the games ruleset.
    @param i: The row position of the move
    @param j: The column position of the move
    @param value: The value to be entered in the moves position (i, j)
    @return: Whether the value already occurs in the square in which the move occurs
    """
    rows = board.m
    columns = board.n

    # convert row and column to the correct square on the board
    introw = math.ceil((i + 1) / rows)
    intcol = math.ceil((j + 1) / columns)

    for p in range(((introw - 1) * rows), (introw * rows)):
        for q in range(((intcol - 1) * columns), (intcol * columns)):
            if board.get(p, q) == value:
                return False
    return True

def check_column_board(board: SudokuBoard, j, value):
    """
    Check whether the value inputted by a move in column position j violates the games ruleset.
    @param j: The column for which to check
    @param value: The value to be entered in the column
    @return: Whether the value already occurs in the column
    """
    for p in range(board.N):
        if board.get(p, j) == value:
            return False
    return True

def check_row_board(board: SudokuBoard, i, value):
    """
    Check whether the value inputted by a move in row position i violates the games ruleset.
    @param i: The row for which to check
    @param value: The value to be entered in the row
    @return: Whether the value already occurs in the row
    """
    for q in range(board.N):
        if board.get(i, q) == value:
            return False
    return True

def solvable(board: SudokuBoard, move: Move):
    i = move.i
    j = move.j
    value = move.value

    return check_row_board(board, i, value) and check_column_board(board, j, value) and check_square_board(board, i, j, value)


def only_square_strat(board: SudokuBoard, move: Move):
    moves = []
    # apply the only square rule to try and find guaranteed moves to fill rows, columns or sections
    for i in range(N):
        # loop over rows and check if a row has 2 empty slots
        empties = []
        options = [i for i in range(1, N+1)]
        for j in range(N):
            if board.get(i, j) is SudokuBoard.empty:
                empties.append((i, j))
            else:
                options.remove(board.get(i, j))
        # if there's exactly 2
        if len(empties) == 2:
            # then check if you can guarantee solve these 2
            # if in both spots both numbers are valid, we cannot be sure which goes where yet
            # otherwise we know that one spot forces one value and the other must for the next
            c1 = [solvable(board, Move(empties[0][0], empties[0][1], options[0])), solvable(board, Move(empties[0][0], empties[0][1], options[1]))] #c11 + c12
            c2 = [solvable(board, Move(empties[1][0], empties[1][1], options[0])), solvable(board, Move(empties[1][0], empties[1][1], options[1]))] #c21 + c22
            if sum(c1) == 2 and sum(c2) == 2:
                return []
            elif sum(c1) == 1 and sum(c2) == 2:
                if c1[0]:
                    return [Move(empties[0][0], empties[0][1], options[0]), Move(empties[1][0], empties[1][1], options[1])]
                else:
                    return [Move(empties[0][0], empties[0][1], options[1]), Move(empties[1][0], empties[1][1], options[0])]
            else: #c1 == 2 c2 == 1 or c1 == 1 and c2 == 1
                if c2[0]:
                    return [Move(empties[1][0], empties[1][1], options[0]), Move(empties[0][0], empties[0][1], options[1])]
                else:
                    return [Move(empties[1][0], empties[1][1], options[1]), Move(empties[0][0], empties[0][1], options[0])]
        else:
            continue
    
    return []
    # TODO: repeat for sections and columns
    # TODO: repeat recursively for > 2 empty spaces
    return []

