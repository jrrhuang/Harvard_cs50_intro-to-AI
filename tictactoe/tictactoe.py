"""
Tic Tac Toe Player
"""

import copy
import math
from math import inf
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    if winner(board) is not None:
        return "Terminal"
    """
    Returns player who has the next turn on a board.
    """
    num_X = 0
    num_O = 0

    for row in board:
        for cell in row:
            if cell == X:
                num_X += 1
            elif cell == O:
                num_O += 1

    if num_X == num_O:
        return X
    elif num_X > num_O:
        return O
    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if winner(board) is not None:
        return "Terminal"

    moves = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                moves.append([i,j])
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    newboard = copy.deepcopy(board)
    newboard[i][j] = player(newboard)
    return newboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #Horizontal
    for row in board:
        if check_same(row):
            return row[0]
    #Vertical
    for i in range(len(board)):
        column = []
        for row in board:
            column.append(row[i])
        if check_same(column):
            return column[0]
    #Diagonal
    i = len(board) - 1
    j = 0
    l_diagonal = []
    r_diagonal = []
    for row in board:
        l_diagonal.append(row[j])
        j += 1
        r_diagonal.append(row[i])
        i -= 1
    if check_same(l_diagonal):
        return l_diagonal[0]
    if check_same(r_diagonal):
        return r_diagonal[0]

    return None

def check_same(lst):
    if all(ele == X for ele in lst) or all(ele == O for ele in lst):
        return True
    else:
        return False

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #Check for 3 in a row
    if winner(board) is not None:
        return True
    #Check if full
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    dict = {}
    if player(board) == X:
        v, count = max_value(board, -inf, inf, 0, dict)
        optimal_moves = []
        for action in actions(board):
            vtemp, count2 = min_value(result(board, action), -inf, inf, 0, dict)
            if v == vtemp:
                optimal_moves.append(action)

    if player(board) == O:
        v, count = min_value(board, -inf, inf, 0, dict)
        optimal_moves = []
        for action in actions(board):
            vtemp, count2 = max_value(result(board,action), -inf, inf, 0, dict)
            if v == vtemp:
                optimal_moves.append(action)
    print(optimal_moves)
    print(v)
    print(count)
    return random.choice(optimal_moves)

def min_value(board, alpha, beta, count, dict):
    key = convert(board)
    if terminal(board):
        return utility(board), count+1
    if key not in dict:
        v = inf

        for action in actions(board):
            vtemp, count = max_value(result(board, action), alpha, beta, count, dict)
            v = min(v, vtemp)
            beta = min(beta, v)
            #if alpha >= beta:
                #break

        dict[key] = v
    return dict[key], count+1

def max_value(board, alpha, beta, count, dict):
    key = convert(board)
    if terminal(board):
        return utility(board), count+1
    if key not in dict:
        v = -inf

        for action in actions(board):
            vtemp, count = min_value(result(board, action), alpha, beta, count, dict)
            v = max(v, vtemp)
            alpha = max(alpha, v)
            #if alpha >= beta:
               # break

        dict[key] = v
    return dict[key], count+1

def convert(board):
    board_tuple = []
    for row in board:
        board_tuple.append(tuple(row))
    return tuple(board_tuple)

print(minimax([[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]))