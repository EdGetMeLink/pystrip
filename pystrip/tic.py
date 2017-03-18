import copy
import random

class Pixel():
    def __init__(self):
        self.color = 0


class TicTacToc():

    def __init__(self, strip=None):
        self.board = [
            Pixel(), Pixel(), Pixel(),
            Pixel(), Pixel(), Pixel(),
            Pixel(), Pixel(), Pixel(),
        ]
        self.player1 = 100
        self.player2 = 200
        self._next_player = self.player1

    def reset_board(self):
        for pixel in self.board:
            pixel.color = 0

    def check_winning(self):
        winning_combos = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
        ]

    def print_board(self):
        for pixel in self.board:
            print(pixel.color)

    @property
    def corners(self):
        return [0, 2, 6, 8]

    @property
    def next_player(self):
        if self._next_player == self.player1:
            self._next_player = self.player2
        elif self._next_player == self.player2:
            self._next_player = self.player1
        return self._next_player

    def available_moves(self):
        return [_ for _, pixel for pixel in enumerate(self.board) if pixel.color == 0]

    def run(self):
        winner = False
        board = copy.copy(self.board)
        first_stone = random.choice(board)
        first_stone.color = self.next_player
        self.print_board()
        while not winner:
            moves = self.available_moves()
            for corner in self.corners:
                if corner in moves:
                    board[corner].color = self.next_player
                    continue
                else:


