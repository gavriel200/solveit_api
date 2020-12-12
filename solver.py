import random

class Solve_sudoku():
    '''
    Solve_sudoko(board = LIST, empty = any value,
    the board value should be a list of 81 values
    representing a sudoku board.
    the empty value is the representation of the empty
    places in the sudoku board list.

    Solve_sudoku is module used to solve / hint for and answer or
    test if the board is valid.

    after creating a board object use the error_check()
    to check if the sudoku board is valid.
    and then use the solve() to solve the sudoku.

    then you have class varubles that yuo will need:
    self.board - you board - after solve() the board is solved.
    self.empty_places - the index of all the empty places.
    self.multiple_answers - wether the solve have multiple answers.
    '''
    def __init__(self, board, empty):
        self.board = board
        self.empty = empty
        self.multiple_answers = False
        self.empty_places = [i for i, n in enumerate(self.board) if n==self.empty]
        self.board = [[1,2,3,4,5,6,7,8,9] if cols==self.empty else [cols] for cols in self.board]

    def error_check(self):
        '''
        error_check() - goes over some test to check wether the 
        board is valid or not.

        use before the solve function to test the board.

        returns True, the error, how to fix if there is an error
        returns False, ok if the board is valid.
        '''
        # check if there are other characters other then the empty char and the numver 1-9.
        for items  in self.board:
            test_items = 0
            for i in range(1, 10):
                if str(items[0]) == str(i):
                    test_items = 1
                    break
            if test_items == 0:
                return True, "bad board item", "check that the board only holdes the numbers 1-9 and the char or int you assinged to be empty place"
        # check that all the squares are valid and that there are no double the numbers
        for checks in [0,3,6,27,30,33,54,57,60]:
            squares_nums = [self.board[cols] for rows in range(checks, checks + 19, 9) for cols in range(rows, rows+3) if len(self.board[cols]) == 1]
            if len(squares_nums) != len(set(str(x) for x in squares_nums)):
                return True, "double error","two of the same numbers in one of the sudoku squares"
        # check that all the rows are valid and that there are no double the numbers
        for checks in range(9):
            rows_nums = [self.board[i] for i in range(checks*9, checks*9+9) if len(self.board[i]) == 1]
            if len(rows_nums) != len(set(str(x) for x in rows_nums)):
                return True, "double error","two of the same numbers in one of the sudoku rows"
        # check that all the cols are valid and that there are no double the numbers
        for checks in range(9):
            cols_nums = [self.board[i] for i in range(checks, checks+73, 9) if len(self.board[i]) == 1]
            if len(cols_nums) != len(set(str(x) for x in cols_nums)):
                return True, "double error","two of the same numbers in one of the sudoku columns"
        # check that the empty value is not 1 - 9
        for checks in range(1,10):
            if self.empty == checks:
                return True, "bad empty value", "the empty value cant be a number from 1-9"
        # check that empty is not False
        if str(self.empty) == "False" and type(self.empty) == type(False):
            return True, "bad empty value", "empty value should not be - false use other value"
        # check that empty is not False
        if str(self.empty) == "True" and type(self.empty) == type(True):
            return True, "bad empty value", "empty value should not be - true use other value"
        # check that the board is not solved already
        if len(self.empty_places) == 0:
            return True, "board is solved", "the board you've send is already solved"
        return False, "ok"

    def __square_check(self, starting_point):
        '''
        __square_check(starting_point = int)

        goes three blockes right and 3 down and check the
        9 blocks square.

        to check every square you will need the starting points:
        0,3,6,27,30,33,54,57,60
        '''
        # get list of all the known numbers in the square.
        # then go over all the lists of "empty" and remove the known numvers
        # and change self.found_changes to 1
        nums_list = [self.board[cols] for rows in range(starting_point, starting_point + 19, 9) for cols in range(rows, rows+3) if len(self.board[cols]) == 1]
        for rows in range(starting_point, starting_point + 19, 9):
            for cols in range(rows, rows+3):
                if len(self.board[cols]) > 1:
                    for numbers in nums_list:
                        if numbers[0] in self.board[cols]:
                            self.board[cols].remove(numbers[0])
                            self.found_changes = 1

    def __row_check(self, starting_point):
        '''
        __row_check(starting_point = int)

        goes and checks all the 9 numbers right from
        the starting point.

        to check every row you will need the starting points:
        0,1,2,3,4,5,6,7,8.
        '''
        # get list of all the known numbers in the square.
        # then go over all the lists of "empty" and remove the known numvers
        # # and change self.found_changes to 1
        nums_list = [self.board[i] for i in range(starting_point*9, starting_point*9+9) if len(self.board[i]) == 1]
        for i in range(starting_point*9, starting_point*9+9):
            if len(self.board[i]) > 1:
                for numbers in nums_list:
                    if numbers[0] in self.board[i]:
                        self.board[i].remove(numbers[0])
                        self.found_changes = 1

    def __col_check(self, starting_point):
        '''
        __col_check(starting_point = int)

        goes and checks 9 numbers down from the
        starting point.

        to check every column you will need the starting points:
        0,1,2,3,4,5,6,7,8.
        '''
        # get list of all the known numbers in the square.
        # then go over all the lists of "empty" and remove the known numvers
        # and change self.found_changes to 1
        nums_list = [self.board[i] for i in range(starting_point, starting_point+73, 9) if len(self.board[i]) == 1]
        for i in range(starting_point, starting_point+73, 9):
            if len(self.board[i]) > 1:
                for numbers in nums_list:
                    if numbers[0] in self.board[i]:
                        self.board[i].remove(numbers[0])
                        self.found_changes = 1

    def solve(self):
        '''
        solve() - the solve function goes over the square, row and col chcek
        function until the self.board is finished.

        if there are multiple answers the solve function chooses the first
        option possible and the sets the self.multiple_answers = True.

        returns False if the board has no final solution.
        '''
        # set the self.fount_changes to 1 to set the value and the start the while loop
        # then go over all the checks - each check makes the self.fount_changes = 1
        # so the loop will continue
        self.found_changes = 1
        while not self.found_changes == 0:
            self.found_changes = 0
            for i in [0,3,6,27,30,33,54,57,60]:
                self.__square_check(i)
            for i in range(9):
                self.__row_check(i)
            for i in range(9):
                self.__col_check(i)
        for items in self.board:
            if len(items) > 1:
                self.multiple_answers = True
                self.board[self.board.index(items)] = [items[0]]
                return self.solve()
        for items in self.board:
            if len(items) < 1:
                return False
        self.board = [items[0] for items in self.board]
        
    def hint(self):
        '''
        hint() -  used to return a hint returns a random place of empty
        and what should be there.

        returns random_place, number that should be there
        '''
        self.random_place = random.choice(self.empty_places)
        return self.random_place, self.board[self.random_place]
