# References:
# https://github.com/google/or-tools/blob/stable/examples/python/sudoku_sat.py
# Lab_DA_05_nQueens.py
# Sudoku online solver: https://sudokuspoiler.com/sudoku/sudoku9

from ortools.sat.python import cp_model


class SolutionPrinter_Sudoku(cp_model.CpSolverSolutionCallback):
    def __init__(self, N, field):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.field_ = field
        self.N_ = N
        self.solutions_ = 0

    def on_solution_callback(self):
        self.solutions_ += 1
        print("Solution " + str(self.solutions_))
        for i in range(self.N_):
            line = "|"
            for j in range(self.N_):
                line += str(self.Value(self.field_[i][j])) + " |"
            print(line)
        print("----------------------------")


def sudoku(N):
    model = cp_model.CpModel()

    # Identify and create the decision variables for the Sudoku puzzle
    # 9x9 grid structure - each cell taking values from 1 to N(inclusive)
    grid = []
    for i in range(N):
        row = []
        for j in range(N):
            # Integer variables for each cell
            row.append(model.NewIntVar(1, N, "cell_" + str(i) + "_" + str(j)))
        grid.append(row)

    # Implement the constraints that specify the digits, given in the puzzle description
    # Ask Alternative: A list of tuples like in the labs?

    # Initial grid (from the sudoku puzzle)
    initial_grid = [
        [0, 0, 0, 0, 0, 0, 0, 3, 0],
        [7, 0, 5, 0, 2, 0, 0, 0, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 0, 0, 0, 4, 0, 0, 2],
        [0, 5, 9, 6, 0, 0, 0, 0, 8],
        [3, 0, 0, 0, 1, 0, 0, 5, 0],
        [5, 7, 0, 0, 6, 0, 1, 0, 0],
        [0, 0, 0, 3, 0, 0, 0, 0, 0],
        [6, 0, 0, 4, 0, 0, 0, 0, 5],
    ]

    # Add constraints for the given values
    for i in range(N):
        for j in range(N):
            # Add only the non-zero values as constraints. Anything else is (0..9) tbd by the solved
            if initial_grid[i][j] != 0:
                model.Add(grid[i][j] == initial_grid[i][j])

    # Define and implement the constraints that no digit can occur twice in any of the rows
    # or columns

    # All different rows
    for i in range(N):
        model.AddAllDifferent(grid[i][j] for j in range(N))

    # All different columns
    for j in range(N):
        model.AddAllDifferent(grid[i][j] for i in range(N))

    # In any of the 3x3 sub-grids
    for i in range(3):
        for j in range(3):
            one_cell = []
            for di in range(3):
                for dj in range(3):
                    one_cell.append(grid[i * 3 + di][j * 3 + dj])

            model.AddAllDifferent(one_cell)

    # Solve the CP-SAT model and determine how many solutions can be found for the above
    # instance
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter_Sudoku(N, grid)
    status = solver.SearchForAllSolutions(model, solution_printer)

    # Output all these solutions
    if status == cp_model.OPTIMAL:
        for i in range(N):
            row_values = []
            for j in range(N):
                row_values.append(int(solver.Value(grid[i][j])))
        print("\nThus, total solutions found: " + str(solution_printer.solutions_))
    else:
        print("No solution")


def main():
    # Grid size (default is 9 x 9)
    N = 9
    sudoku(N)


main()
