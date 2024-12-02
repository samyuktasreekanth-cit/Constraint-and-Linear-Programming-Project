import pandas as pd
import numpy as np
from ortools.sat.python import cp_model


# reference: Lecture_DA_10_Linear_constraints.pdf
# reference: https://sparkbyexamples.com/pandas/pandas-read-excel-with-examples/
# ^ set the first column as the index of the df3_dependencies. So its easier to see the relationship btwn the two projects


class ProjectPlanningSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, projects_to_take_on, contractor_project_month, profit_margin_expr):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._projects_to_take_on = projects_to_take_on
        self._contractor_project_month = contractor_project_month
        self._profit_margin_expr = profit_margin_expr
        self._solution_count = 0

    def on_solution_callback(self):
        self._solution_count += 1
        print('Solution ' + str(self._solution_count))
        print('Projects taken on:')
        for project, var in self._projects_to_take_on.items():
            if self.Value(var):
                print(project)
        print('Contractor work/duration:')
        for (contractor, project, job, month), var in self._contractor_project_month.items():
            if self.Value(var):
                print("Contractor " + contractor + " works on " + project + "(" + job + ")" + " in " " month")
        print('Profit margin: ' + str(self.Value(self._profit_margin_expr)))

        print()

    def solution_count(self):
        return self._solution_count


def project_planning(file_path):
    # --------------------------------------------A--------------------------------------------------
    # Load the excel file Assignment_DA_1_data.xlsx and extract all relevant information [1 point].
    # -----------------------------------------------------------------------------------------------

    # Extract all the relevant information
    xls = pd.ExcelFile(file_path)
    df1_projects = pd.read_excel(xls, 'Projects')
    df2_quotes = pd.read_excel(xls, 'Quotes')
    df3_dependencies = pd.read_excel(xls, 'Dependencies', index_col=0)
    df4_value = pd.read_excel(xls, 'Value', index_col=0)

    # Identify and create solutions in a CP-SAT model that you need to decide what projects to take on
    model = cp_model.CpModel()

    # ----------------------------------------------------------------------------------------------
    #  Make sure to use the data from the file in your code, please do not hardcode any values that
    #  can be read from the file
    # -----------------------------------------------------------------------------------------------

    # Have a list of project names
    # ['Project A', 'Project B', 'Project C', 'Project D', 'Project E', 'Project F', 'Project G', 'Project H', 'Project I']
    projects = list(df1_projects[df1_projects.columns[0]])

    # Have a list of months
    # ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12']
    months = list(df1_projects.columns[1:])

    # Have a list of contractors
    # ['Contractor A', 'Contractor B', 'Contractor C', 'Contractor D', 'Contractor E', 'Contractor F', 'Contractor G', 'Contractor H', 'Contractor I', 'Contractor J', 'Contractor K']
    contractors = list(df2_quotes[df2_quotes.columns[0]])

    # Have a list of jobs
    # ['Job A', 'Job B', 'Job C', 'Job D', 'Job E', 'Job F', 'Job G', 'Job H', 'Job I', 'Job J', 'Job K', 'Job L', 'Job M']
    jobs = list(df2_quotes.columns[1:])

    # --------------------------------------------B--------------------------------------------------
    # Identify and create the decision variables in a CP-SAT model that you need to decide what
    # projects to take on [1 point].
    # -----------------------------------------------------------------------------------------------

    # Project: Decision variables for what projects to take on
    projects_to_take_on = {}
    for project in projects:
        projects_to_take_on[project] = model.NewBoolVar(project)

    # -----------------------------------------------------------------------------------------------
    # Also identify and create the decision variables you need to
    # decide, which contractor is working on which project and when. Make sure to consider that
    # not all contractors are qualified to work on all jobs
    # -----------------------------------------------------------------------------------------------

    # Decision variable for which contractor is working on which project and when
    contractor_project_month = {}
    for project in projects:
        for month in months:
            # A list for a job associated with each project and month according to the given Excel sheet 'Projects'
            job_for_project_month = list(
                df1_projects.loc[df1_projects[df1_projects.columns[0]] == project, month].dropna())
            # print(job_for_project_month)
            for job in job_for_project_month:
                for contractor in contractors:
                    # check if a quote is associated with each contractor and job for the Excel sheet 'Quotes'
                    quotes_for_contractor_job = \
                        df2_quotes.loc[df2_quotes[df2_quotes.columns[0]] == contractor, job].values[0]
                    # Make sure to consider that not all contractors are qualified to work on all jobs
                    # Logic:  A quote exists for the contractor in the Excel cell if he is qualified, else it is empty
                    if quotes_for_contractor_job is not np.nan:
                        # Contractor + Project (including job) + Month
                        # so will look like: "Contractor K + Project I + Job K + M12"
                        contractor_project_month[(contractor, project, job, month)] = model.NewBoolVar(
                            contractor + " + " + project + " + " + job + " + " + month)

    # note: using dropna() +  not np.nan as the alternative to fillna() made it too complicated

    # -----------------------------------------------------------------------------------------------
    #  and that projects do not run over all months [3 points].
    # -----------------------------------------------------------------------------------------------

    # Project + Month : Decision variables for project in that month
    project_month = {}
    for project in projects:
        variables = {}
        for month in months:
            variables[month] = model.NewBoolVar(project + " + " + month)
        project_month[project] = variables

    # --------------------------------------------C--------------------------------------------------
    #  Define and implement the constraint that a contractor cannot work on two projects
    #  simultaneously [3 points].
    # -----------------------------------------------------------------------------------------------

    # Decision variable: contractor + month
    contractor_month = {}
    for contractor in contractors:
        variables = {}
        for month in months:
            variables[month] = model.NewBoolVar(contractor + " + " + month + " + ")
        contractor_month[contractor] = variables

    # Constraint:  A contractor can only work on one project in a month
    for contractor in contractors:
        for month in months:
            model.Add(sum(contractor_project_month[(contractor, project, job, month)]
                          for project in projects for job in jobs
                          if (contractor, project, job, month) in contractor_project_month) <= 1)

    # --------------------------------------------D--------------------------------------------------
    # Define and implement the constraint that if a project is accepted to be delivered then
    # exactly one contractor per job of the project needs to work on it [4 points].
    # -----------------------------------------------------------------------------------------------

    # using the concept of Channelling Constraint from the canvas slides
    for project in projects:
        for month in months:
            # same logic as before: from the Projects sheet, filter and clean the data nan are empty lists instead
            job_for_project_month = list(
                df1_projects.loc[df1_projects[df1_projects.columns[0]] == project, month].dropna())
            # print(job_for_project_month)
            contractor_assignments = []
            for contractor in contractors:
                # see if contractor is qualified for the job
                if (contractor, project, job, month) in contractor_project_month:
                    contractor_assignments.append(contractor_project_month[(contractor, project, job, month)])
            # constraint: only one contractpr is assigned if the particular project is taken on
            if contractor_assignments:
                model.Add(sum(contractor_assignments) == 1).OnlyEnforceIf(projects_to_take_on[project])

    # --------------------------------------------E--------------------------------------------------
    #  Define and implement the constraint that if a project is not taken on then no one should be
    #  contracted to work on it [4 points].
    # -----------------------------------------------------------------------------------------------

    for project in projects:
        for job in jobs:
            for contractor in contractors:
                for month in months:
                    # Logic: if (contractor, project, job, month) combi is valid (exists in contractor_project_month)
                    if (contractor, project, job, month) in contractor_project_month:
                        # Logic:If the project is NOT taken, the contractor is NOT assigned to the job
                        model.Add(contractor_project_month[(contractor, project, job, month)] == 0).OnlyEnforceIf(
                            projects_to_take_on[project].Not())

    # --------------------------------------------F--------------------------------------------------
    #  Define and implement the project dependency and project conflict constraints
    # -----------------------------------------------------------------------------------------------
    for project_row in projects:
        for project_col in projects:
            # print(df3_dependencies.at[project_row, project_col])
            # as long as it's not in conflict with itself
            if project_row != project_col:
                # dependent. (e.g. Project B can only be taken on, if also Project A is taken on)
                if df3_dependencies.at[project_row, project_col] == "required":
                    model.Add(projects_to_take_on[project_row] <= projects_to_take_on[project_col])
                    # print("Required constraints: " + str(project_row) + " requires " + str(project_col))
                # if they conflict, none can be taken
                elif df3_dependencies.at[project_row, project_col] == 'conflict':
                    model.Add(projects_to_take_on[project_row] + projects_to_take_on[project_col] <= 1)
                    # print("Conflict constraint: " + str(project_row) + " conflicts with " + str(project_col))

    # --------------------------------------------G--------------------------------------------------
    # Define and implement the constraint that the profit margin, i.e. the difference between the
    # value of all delivered projects and the cost of all required subcontractors, is at least €2160 [5
    # points].
    # -----------------------------------------------------------------------------------------------

    # dictionary where keys:project names and values:values
    project_values = df4_value['Value'].to_dict()
    # {'Project A': 500, 'Project B': 300, 'Project C': 400, 'Project D': 1000, 'Project E': 2000, 'Project F': 100, 'Project G': 1500, 'Project H': 1000, 'Project I': 1000}
    # print(project_values)

    # Calculate the total value of all delivered projects
    total_delivered_value = sum(project_values[project] * projects_to_take_on[project] for project in project_values)
    # print(total_delivered_value)

    # Calculate the total value of all delivered projects
    total_delivered_value = sum(df4_value.at[project, 'Value'] * projects_to_take_on[project] for project in projects)

    # Set the first column as the index if it's not already.
    # getting the error KeyError: 'Contractor A' if i dont do this
    df2_quotes.set_index(df2_quotes.columns[0], inplace=True)

    # Calculate the total subcontractor cost
    total_subcontractor_cost_expr = model.NewIntVar(0, 1000000, 'total_subcontractor_cost')
    subcontractor_costs = []
    for (contractor, project, job, month), variable in contractor_project_month.items():
        # Skip this contractor-job pair cause no quote available
        # same logic as before
        if pd.isna(df2_quotes.at[contractor, job]):
            continue
        else:
            job_cost = int(df2_quotes.at[contractor, job])
            subcontractor_costs.append(job_cost * variable)

    model.Add(total_subcontractor_cost_expr == sum(subcontractor_costs))

    # Profit margin constraint
    profit_margin_expr = total_delivered_value - total_subcontractor_cost_expr
    model.Add(profit_margin_expr >= 2160)

    # --------------------------------------------H--------------------------------------------------
    # Solve the CP-SAT model and determine how many possible solutions satisfy all the
    # constraints [1 point]. For each solution, determine what projects are taken on [1 point],
    # which contractors work on which projects in which month [1 point], and what is the profit
    # margin [1 point]
    # -----------------------------------------------------------------------------------------------
    solver = cp_model.CpSolver()
    solution_printer = ProjectPlanningSolutionPrinter(projects_to_take_on, contractor_project_month, profit_margin_expr)

    # Search for all solutions

    # To many solutions if using solver.SearchForAllSolutions
    status = solver.Solve(model, solution_printer)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Total solutions found: ' + str(solution_printer.solution_count()))
    else:
        print('No solution found.')



def main():
    # Load the Excel file 'Assignment_DA_1_data.xlsx'
    # replace as needed if there is a different filepath or filename
    file_path = "datasets/Assignment_DA_1_data.xlsx"
    project_planning(file_path)


main()
