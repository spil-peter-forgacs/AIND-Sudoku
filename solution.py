"""
Solve a Sudoku
"""

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

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
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
        result[boxes[i]] = current if current != "." else cols
        #result = assign_value(result, boxes[i], current if current != "." else cols)

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

    import copy
    result = copy.deepcopy(values)

    # All elements.
    for i in boxes:
        current = values[i]

        # If the current element has only one number.
        if len(current) == 1:
            currentRow = i[0]
            currentCol = i[1]

            # Filter out cols.
            for col in cols:
                if col != currentCol:
                    result[currentRow + col] = result[currentRow + col].replace(current, "")
            # Filter out rows.
            for row in rows:
                if row != currentRow:
                    result[row + currentCol] = result[row + currentCol].replace(current, "")
            # Filter out squares.
            # Find the square unit.
            for square in square_units:
                if i in square:
                    # Filter the square.
                    for squareElement in square:
                        if squareElement != i:
                            result[squareElement] = result[squareElement].replace(current, "")

    return result

def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """

    import copy
    result = copy.deepcopy(values)

    # Check all unit lists.
    for unit in unitlist:
        # Check all available elements.
        # From 1 to 9.
        for i in range(1, len(cols)+1):
            found = ''
            unique = True
            for unitElement in unit:
                if str(i) in values[unitElement]:
                    if found == '':
                        found = unitElement
                    else:
                        unique = False
            # If the element is found and unique, then change the value.
            if unique and found != '':
                result[found] = str(i)

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
        import copy
        result = copy.deepcopy(values)

        result[fewest] = i
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

    # Global variables.

    global rows
    global cols
    global boxes
    global row_units
    global column_units
    global square_units
    global unitlist
    global units
    global peers

    rows = 'ABCDEFGHI'
    cols = '123456789'

    boxes = cross(rows, cols)

    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    unitlist = row_units + column_units + square_units

    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    
    # Solve the puzzle
    return search(grid_values(grid))

if __name__ == '__main__':
    """
    Main entry points.
    """

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
