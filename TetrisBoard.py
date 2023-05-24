import numpy as np

class TetrisBoard:
    def __init__(self):
        self.board = np.zeros((20, 10), dtype=int)

    def add_piece(self, piece, position):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    self.board[position[0] + y, position[1] + x] = 1

    def does_piece_fit(self, piece, position):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    if position[0] + y >= self.board.shape[0] or position[1] + x >= self.board.shape[1]:
                        return False
                    if self.board[position[0] + y, position[1] + x] == 1:
                        return False
        return True

    def clear_full_rows(self):
        while True:
            for y, row in enumerate(self.board):
                if all(cell == 1 for cell in row):
                    self.board = np.delete(self.board, y, axis=0)
                    # insert new row at last index which is the top of the board
                    self.board = np.insert(self.board, self.board.shape[0], 0, axis=0)
                    break
                if y == self.board.shape[0] - 1:
                    return
        
