#! usr/bin/python
from copy import deepcopy
from enum import Enum


class Type(Enum):
    CORNER = 0
    EDGE = 1
    FULLFIL = 2


class Puzzle:
    def __init__(self, id: int, a: int, b: int, c: int, d: int):
        self.id = id
        self.rotation = 0
        self.left = a
        self.top = b
        self.right = c
        self.bottom = d
        self.is_corner = (
            self.left == 0 and self.top == 0
        ) or (
            self.top == 0 and self.right == 0
        ) or (
            self.right == 0 and self.bottom == 0
        ) or (
            self.bottom == 0 and self.left == 0
        )
        self.is_edge = not self.is_corner and (
            self.left == 0 or self.top == 0 or
            self.right == 0 or self.bottom == 0
        )
        if self.is_corner:
            self.type = Type.CORNER
        elif self.is_edge:
            self.type = Type.EDGE
        else:
            self.type = Type.FULLFIL

    def rotate(self, degree=None):
        if degree is not None:
            while self.rotation != degree:
                self.rotation = (self.rotation + 90) % 360
                temp = self.left
                self.left = self.bottom
                self.bottom = self.right
                self.right = self.top
                self.top = temp
        else:
            self.rotation = (self.rotation + 90) % 360
            temp = self.left
            self.left = self.bottom
            self.bottom = self.right
            self.right = self.top
            self.top = temp


class Field:
    def __init__(self, debug: bool = True):
        self.n = 0
        self.m = 0
        self.field = None
        self.puzzle = []
        self.corners = []
        self.edges = []
        self.fills = []
        self.solutions = []
        self.rotations = []
        self.solutions_counter = 0
        self.debug = debug

    def load(self, n: int, m: int):
        self.n = n
        self.m = m
        self.field = [[None for _ in range(m)] for _ in range(n)]

    def loadpuzzle(self, description: tuple[int, int, int, int, int]):
        id, left, top, right, bottom = description
        puzzle = Puzzle(id, left, top, right, bottom)
        self.puzzle.append(puzzle)
        if puzzle.is_corner:
            self.corners.append(puzzle)
        elif puzzle.is_edge:
            self.edges.append(puzzle)
        else:
            self.fills.append(puzzle)

    def get_cell_type(self, row: int, col: int) -> Type:
        if (row == 0 or row == self.n - 1) and (col == 0 or col == self.m - 1):
            return Type.CORNER
        if row == 0 or row == self.n - 1 or col == 0 or col == self.m - 1:
            return Type.EDGE
        return Type.FULLFIL

    def check_if_correct(self, row: int, col: int, cell_type: Type, puzzle: Puzzle) -> bool:
        correct = True
        if cell_type == Type.CORNER:
            if row == 0:
                if col == 0:
                    correct = puzzle.top == 0 and puzzle.left == 0
                else:
                    correct = (
                        puzzle.top == 0 and puzzle.right == 0 and
                        puzzle.left == self.puzzle[self.field[row][col - 1]].right
                    )
            else:
                if col == 0:
                    correct = (
                        puzzle.left == 0 and puzzle.bottom == 0 and
                        puzzle.top == self.puzzle[self.field[row - 1][col]].bottom
                    )
                else:
                    correct = (
                        puzzle.right == 0 and puzzle.bottom == 0 and
                        puzzle.left == self.puzzle[self.field[row][col - 1]].right
                    )
        elif cell_type == Type.EDGE:
            if row == 0:
                correct = (
                    puzzle.top == 0 and
                    puzzle.left == self.puzzle[self.field[row][col - 1]].right
                )
            elif row == self.n - 1:
                correct = (
                    puzzle.bottom == 0 and
                    puzzle.top == self.puzzle[self.field[row - 1][col]].bottom and
                    puzzle.left == self.puzzle[self.field[row][col - 1]].right
                )
            elif col == 0:
                correct = (
                    puzzle.left == 0 and
                    puzzle.top == self.puzzle[self.field[row - 1][col]].bottom
                )
            elif col == self.m - 1:
                correct = (
                    puzzle.right == 0 and
                    puzzle.left == self.puzzle[self.field[row][col - 1]].right and
                    puzzle.top == self.puzzle[self.field[row - 1][col]].bottom
                )
            else:
                assert 'smth was going wrong'
        else:
            correct = (
                self.puzzle[self.field[row][col - 1]].right == puzzle.left and
                self.puzzle[self.field[row - 1][col]].bottom == puzzle.top
            )
        return correct

    def solve(self, row: int, col: int, used: list[Puzzle]):
        if row == self.n:  # and col == self.m:
            if self.solutions:
                _, solution = list(zip(*self.solutions))
                if self.field in solution:
                    return
            if self.debug:
                # debug print
                print('solution found')
                for i in range(self.n):
                    for j in range(self.m):
                        print(f'{(self.field[i][j] + 1):2}', end=' ')
                    print()
                print('*'*14)
                # end of debug print
            # find new solution
            self.solutions_counter += 1
            solution = deepcopy(self.field)
            self.solutions.append((self.solutions_counter, solution))
            rotation = [None]*(self.m*self.n)
            for puzzle in self.puzzle:
                rotation[puzzle.id] = puzzle.rotation
            self.rotations.append(rotation)
            # add solution rotated clockwise 3 times
            for _ in range(3):
                solution = [list(row) for row in zip(*solution[::-1])]
                self.solutions.append((self.solutions_counter, solution))
                # self.rotations.append(rotation)
            return
        cell_type = self.get_cell_type(row, col)
        for puzzle in self.puzzle:
            if puzzle in used:
                continue
            if puzzle.type != cell_type:
                continue
            for _ in range(4):
                puzzle.rotate()
                if self.check_if_correct(row, col, cell_type, puzzle):
                    self.field[row][col] = puzzle.id
                    used.append(puzzle)
                    next_row = row
                    next_col = col + 1
                    if next_col == self.m:
                        next_row += 1
                        next_col = 0
                    self.solve(next_row, next_col, used)
                    used.pop()
                    self.field[row][col] = None

    def print_solutions(self, verbose: bool = False):
        numbers = set()
        if not verbose:
            for number, solution in self.solutions:
                if number not in numbers:
                    print(f'solution # {number}:')
                    numbers.add(number)
                    for row in range(self.n):
                        for col in range(self.m):
                            print(f'{(solution[row][col] + 1):3}', end=' ')
                        print()
                    print('')
        else:
            for number, solution in self.solutions:
                if number not in numbers:
                    print(f'solution # {number}:')
                    numbers.add(number)
                    for puzzle in self.puzzle:
                        puzzle.rotate(self.rotations[number - 1][puzzle.id])
                    # l1, l2, l3, l4, l5 = '', '', '', '', ''
                    for row in range(self.n):
                        l1, l2, l3, l4, l5 = '', '', '', '', ''
                        for col in range(self.m):
                            l1 += f'┏━━━━━━━' + ('┓' if col == self.m - 1 else '')
                            l2 += f'┃   {self.puzzle[solution[row][col]].top}   ' + ('┃' if col == self.m - 1 else '')
                            l3 += f'┃{self.puzzle[solution[row][col]].left} {(solution[row][col] + 1):3} {self.puzzle[solution[row][col]].right}' + ('┃' if col == self.m - 1 else '')
                            l4 += f'┃   {self.puzzle[solution[row][col]].bottom}   ' + ('┃' if col == self.m - 1 else '')
                            l5 += f'┗━━━━━━━'  + ('┛' if col == self.m - 1 else '')
                        if row == 0:
                            print(f'{l1}\n{l2}\n{l3}\n{l4}\n{l5}')
                        else:
                            print(f'{l2}\n{l3}\n{l4}\n{l5}')
                    print('')


if __name__ == '__main__':
    n, m = map(int, input().split())
    game = Field(debug=False)
    game.load(n, m)
    for id in range(n*m):
        a, b, c, d = map(int, input().split())
        game.loadpuzzle((id, a, b, c, d))
    game.solve(0, 0, [])
    game.print_solutions(verbose=False)
