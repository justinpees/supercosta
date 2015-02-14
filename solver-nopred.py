#
# The following code is public domain (written in 2005 by Nick Smallbone)
# It can be found at http://www.8325.org/sudoku/
#

# It works by keeping track of which numbers can be used to fill the remaining
# cells in each row, column and block. It then will only fill a cell with a
# number that is valid for that row, column and block.

# On every recursion, it chooses the cell with the least possible number
# available to choose from. This has the rather nice effect that impossible
# cells are noticed straight away without any special cases, and cells with
# only one possibility are filled in straight away.

import sys

#
# First, some functions to manipulate bitfields as sets
#

# Returns the number of 1 bits in a bitfield
def bitCount(bits):
    result = 0
    while bits != 0:
        if bits % 2 == 1:
            result += 1
        bits /= 2
    return result

# Gives a bitfield with only number num set
def bitFor(num):
    return 1 << (num - 1)

# Generates a list from a bitfield
def bitList(bits):
    current = 1
    r = []
    while bits != 0:
        if bits % 2 == 1:
            r.append(current)
        bits /= 2
        current += 1

    return r

class Puzzle:
    def __init__(self):
        # Make a blank puzzle

        # rows[i] stores the set of possible values that an unset cell in
        # row i could take. Similarly for cols and blocks.
        # cells stores the cells which have been set so far. If they are
        # unset, the value is None, otherwise it is a number from 0 to 9.
        self.rows = [ 0x1ff for i in range(9) ]
        self.cols = [ 0x1ff for i in range(9) ]
        self.blocks = [[ 0x1ff for i in range(3)] for j in range(3)]
        self.cells = [[ None for i in range(9)] for j in range(9)]

    def candidates(self, row, col):
        # Return the possible values which this cell could have
        assert(self.cells[row][col] == None)
        return self.rows[row] & self.cols[col] & self.blocks[row/3][col/3]

    def set(self, row, col, num):
        # Fill in the cell at (row, col) with value num 

        bit = bitFor(num)
        # Make sure that the bit is acceptable
        assert self.cells[row][col] == None
        assert self.candidates(row, col) & bit != 0

        # No cell in this row, column or block can now have this value
        self.rows[row] &= ~bit
        self.cols[col] &= ~bit
        self.blocks[row/3][col/3] &= ~bit

        # and set it
        self.cells[row][col] = num

    def unset(self, row, col, num):
        # Erase the cell at (row, col), updating rows, cols and blocks.

        bit = bitFor(num)

        # Make sure it was already set        
        assert self.cells[row][col] == num
        assert self.rows[row] & self.cols[col] & self.blocks[row/3][col/3] & bit == 0

        self.rows[row] |= bit
        self.cols[col] |= bit
        self.blocks[row/3][col/3] |= bit
        self.cells[row][col] = None

    def findMin(self):
        # Pick the cell with the smallest number of candidates.
        # Returns None if there are no unset cells.

        min = None
        minPos = None
        for i in range(9):
            for j in range(9):
                if self.cells[i][j] == None:
                    if min == None or bitCount(self.candidates(i, j)) < min:
                        min = bitCount(self.candidates(i, j))
                        minPos = (i, j)

        return minPos

# Tries to solve the puzzle in-place.
def solve(puzzle):
    min = puzzle.findMin()

    if min is None:
        return True

    # We'll brute force on this cell
    (i, j) = min

    for num in bitList(puzzle.candidates(i, j)):
        # Try num on cell (i, j)
        puzzle.set(i, j, num)

        if solve(puzzle):
            return True

        puzzle.unset(i, j, num)

    # We've exhausted all possibilities so the puzzle is unsolvable
    return False

# Read a puzzle from a given file
def readPuzzle(file):
    puzzle = Puzzle()
    for i in range(9):
        line = file.readline()
        for j in range(9):
            c = line[j]
            if ord(c) >= ord('1') and ord(c) <= ord('9'):
                if puzzle.candidates(i, j) & bitFor(int(c)) == 0:
                    sys.exit(0)
                else:
                    puzzle.set(i, j, int(c))
            elif c == '.':
                pass
            else:
                raise Exception, "bad input: " + c
    return puzzle

def printPuzzle(puzzle):
    for i in range(9):
        s = ""
        for j in range(9):
            if puzzle.cells[i][j] == None:
                s += " "
            else:
                s += str(puzzle.cells[i][j])
        print s

# Solve and print out a puzzle
def outputSolution(puzzle):
    if solve(puzzle):
        printPuzzle(puzzle)

if __name__ == "__main__":
    try:
        outputSolution(readPuzzle(sys.stdin))
    except KeyboardInterrupt:
        print "Interrupted"
