# Constraint-Programming-Project
This is the Decision Analytics Module from the Masters in Artificial Intelligence Course involving concepts in Linear and Constraint Programming. 

Technology and Tools:
CP-SAT model (OR-tools), Python, Numpy and Pandas


# Constraint Programming


Task 1 (task1.py) - Develop a constraint satisfaction model that solves the following logical puzzle:
James, Daniel, Emily, and Sophie go out for dinner. They all order a starter, a main course, a desert, and drinks and they want to order as many different things as possible. 

The carpaccio starter is not combined with the vegan pie as main course and the filet steak main course is not followed by ice cream as desert. (1) 

Emily does not have prawn cocktail or onion soup as starter and none of the men has beer or coke to drink. (2) 

The person having prawn cocktail as starter has baked mackerel as main course and the filet steak main course works well with the red wine. (3) 

One of the men has white wine as drink and one of the women drinks coke. (4) 

The vegan pie main always comes with mushroom tart as starter and vice versa; also, the onion soup and filet steak are always served together. (5) 

Emily orders beer as drink or has fried chicken as main and ice cream as desert; James orders coke as drink or has onion soup as starter and filet steak as main. (6) 

Sophie orders chocolate cake but does not drink beer nor likes fried chicken; Daniel orders apple crumble for dessert but has neither carpaccio nor mushroom tart as starter. (7) 

Who has tiramisu for dessert? 

A. Identify the objects, attributes and predicates for the puzzle and create the decision variables in a CP-SAT model. 

B. For each of the seven sentences in the puzzle define the explicit constraints contained in the sentences in conjunctive normal form and add them to the CP-SAT model. 

C. The puzzle also contains some implicit constraints. Define and implement these implicit constraints in the CP-SAT model.
 
D. Solve the CP-SAT model and determine the starter, main course, dessert, and drink ordered by each of the diners. 

Task 2 (sudoku_task2.py) - Sudoku 

Develop a constraint satisfaction model for solving a given Sudoku puzzle. The goal is to fill the remaining digits into grid so that no digit occurs twice in any of the rows, in any of the columns, or in any of the 3x3 sub-grids.

A. Identify and crate the decision variables for the Sudoku puzzle in a CP-SAT model and implement the constraints that specify the digits, which are already given in the puzzle specification. 
B. Define and implement the constraints that no digit can occur twice in any of the rows or columns, or in any of the 3x3 sub-grids. 
C. Solve the CP-SAT model and determine how many solutions can be found for the above instance. Output all these solutions.

Task 3 (project_planning_task3.py) - project planning


Develop a constraint satisfaction problem model for deciding what projects can be taken on and what companies need to be contracted to deliver on these projects. Using the .xlsx file involving Projects, Quotes, Dependencies and Value sheets to extract and use the data. 

Dataset Excel : Assignment_DA_1_data.xlsx



