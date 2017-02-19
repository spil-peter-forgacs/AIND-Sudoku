"""
Solve a Sudoku
"""

# Global variables.

rows = 'ABCDEFGHI'
cols = '123456789'
# toSize = 10 in case of 9x9 Sudoku puzzle
toSize = len(rows)+1

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[rows[i-1] + str(i) for i in range(1, toSize)], [rows[i-1] + str(toSize - i) for i in range(1, toSize)]]
unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    for unit in unitlist:
        for box in unit:
            currentValues = values[box]
            # Check, if it has two numbers. So possible twin value.
            if len(currentValues) == 2:
                # Check, if there is a twin.
                twins = 0
                # Collect not twin boxes.
                others = []
                for otherBox in unit:
                    if currentValues == values[otherBox]:
                        twins += 1
                    else:
                        others.append(otherBox)

                # Remove twin values from other boxes.
                if twins == 2:
                    for otherBox in others:
                        for currentValue in currentValues:
                            # Assign and visualize
                            assign_value(values, otherBox, values[otherBox].replace(currentValue,''))

    return values

def sub_group_exclusion(values):
    """
    Eliminate values using the Sub-group exclusion rule.
    It can happen, when e.g. a square unit has a number in only on one row or column.
    In this case the other boxes in the row or column can't have this number.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the Sub-group exclusion rule applied.
    """

    for unit in unitlist:
        for digit in '123456789':
            # Collect the unit boxes, where a certain number presents.
            found = [box for box in unit if digit in values[box]]
            # If there is more, then one, then worth to check other units too.
            if len(found) > 1:
                for otherUnit in unitlist:
                    if unit != otherUnit:
                        # Check, if all the boxes - containing the number - are in the other unit too.
                        contains = [element for element in found if element in otherUnit]
                        # If yes, then that number shouldn't be in other boxes - in the other unit.
                        if len(contains) == len(found):
                            for otherBox in otherUnit:
                                if not (otherBox in found):
                                    # Assign and visualize
                                    assign_value(values, otherBox, values[otherBox].replace(digit,''))

    return values

def grid_values(grid, basicFormat=False):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties. E.g.:
    return {
        'A1': '123456789',
        'A2': '123456789',
        'A3': '3',
        'A4': '123456789',
        'A5': '2',
        'I9': '123456789',
        ...
    }
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    result = {}

    for i in range(len(boxes)):
        current = grid[i]
        result[boxes[i]] = current if current != "." or basicFormat else cols

    return result

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """

    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """

    result = values.copy()

    # All elements.
    for box in boxes:
        digit = values[box]

        # If the current element has only one number.
        if len(digit) == 1:
            for peer in peers[box]:
                # Assign and visualize
                assign_value(result, peer, result[peer].replace(digit,''))

    result = naked_twins(result)
    result = sub_group_exclusion(result)

    return result



def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """

    result = values.copy()

    for unit in unitlist:
        # All numbers.
        for i in range(1, 10):
            digit = str(i)
            found = ''
            unique = True
            for unitElement in unit:
                if digit in values[unitElement]:
                    unique = (found == '')
                    found = unitElement
            # Is this number found and unique?
            if unique and found != '':
                result[found] = digit

    return result

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.

    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False

    # Check, if it was a solution.
    solved_values = len([box for box in values.keys() if len(values[box]) == 1])
    if solved_values == len(boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    fewest = ''
    for box in values.keys():
        boxValues = len(values[box])
        if boxValues > 1:
            if fewest == '' or boxValues < len(values[fewest]):
                fewest = box

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for i in values[fewest]:
        result = values.copy()

        # Assign and visualize
        assign_value(result, fewest, i)

        solution = search(result)

        if solution:
            return solution

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    
    # Solve the puzzle
    return search(grid_values(grid))

if __name__ == '__main__':
    """
    Main entry points.
    """

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    print("Original state:")
    basicFormat = True
    display(grid_values(diag_sudoku_grid, basicFormat))

    solution = solve(diag_sudoku_grid)
    if solution:
        print("Solution:")
        display(solution)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
