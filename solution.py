import logging
assignments = []
logging.info("Logs")

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

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

    new_values = values.copy()
    naked_twins = []
    for box in new_values:
        if len(new_values[box]) == 2:
            #print(new_values[box])
            for peer in peers[box]:
                #print(peer)
                if box < peer and new_values[peer] == new_values[box]:
                    naked_twins.append([box, peer])
    #print(naked_twins)                
    for twin in naked_twins:
        units = [u for u in unitlist if twin[0] in u and twin[1] in u]
        #print(units)
        for unit in units:
            for box in unit:
                if box != twin[0] and box != twin[1]:
                    
                    new_values[box] = new_values[box].replace(new_values[twin[0]][0], '')
                    assign_value(new_values, box, new_values[box]) 
                    
                    new_values[box] = new_values[box].replace(new_values[twin[0]][1], '')
                    assign_value(new_values, box, new_values[box]) 
                    
    if len([box for box in new_values.keys() if len(new_values[box]) == 0]):
        return False
    return new_values

def cross(A, B):
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
#diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']]
diagonal_units = [[r+c for r,c in zip(rows,cols)], [r+c for r,c in zip(rows,cols[::-1])]]
unitlist = row_units + column_units + square_units+diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
#diagonal_units = dict((s, [u for u in unitlist if s in u])
#             for s in boxes)
#diagonal_peers = dict((s, set(sum(diagonal_units[s],[]))-set([s]))
#             for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

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
    new_values = values.copy()
    solved_values = [box for box in new_values.keys() if len(new_values[box]) == 1]
    for box in solved_values:
        digit = new_values[box]
        for peer in peers[box]:
            new_values[peer] = new_values[peer].replace(digit,'')
            assign_value(new_values, peer, new_values[peer])
    return new_values

def only_choice(values):
    new_values = values.copy()
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in new_values[box]]
            if len(dplaces) == 1:
                new_values[dplaces[0]] = digit
                assign_value(new_values, dplaces[0], new_values[dplaces[0]])
    return new_values

def reduce_puzzle(values):
    new_values=values.copy()
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in new_values.keys() if len(new_values[box]) == 1])
        new_values = eliminate(new_values)
        new_values = only_choice(new_values)
      # new_values = naked_twins(new_values)
        solved_values_after = len([box for box in new_values.keys() if len(new_values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in new_values.keys() if len(new_values[box]) == 0]):
            return False
    return new_values

def search(values):
    new_values = reduce_puzzle(values.copy())
    if new_values is False:
        return False ## Failed earlier
    if all(len(new_values[s]) == 1 for s in boxes): 
        return new_values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(new_values[s]), s) for s in boxes if len(new_values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in new_values[s]:
        new_sudoku = new_values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    grid = grid_values(grid)
    return search(grid)

if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid =  '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
