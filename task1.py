from ortools.sat.python import cp_model

# Identify the objects, attributes and predicates for the puzzle
# And create the decision variables in a CP-SAT model

# --------------------------------------------------------------------
#                      Domain Object - persons
# --------------------------------------------------------------------

persons = ["James", "Daniel", "Emily", "Sophie"]

# --------------------------------------------------------------------
#                      Domain Attributes
# --------------------------------------------------------------------
starters = ["carpaccio", "prawn cocktail", "onion soup", "mushroom tart"]
mains = ["vegan pie", "filet steak", "baked mackerel", "fried chicken"]
deserts = ["ice cream", "chocolate cake", "apple crumble", "tiramisu"]
drinks = ["beer", "coke", "red wine", "white wine"]


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, solver, starter, main, desert, drink):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solver = solver
        self.starter_ = starter
        self.main_ = main
        self.desert_ = desert
        self.drink_ = drink
        self.solutions_ = 0

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)

        for person in persons:
            print(" - " + person + ":")
            for starter in starters:
                if (self.Value(self.starter_[person][starter])):
                    print("    - ", starter)
            for main in mains:
                if (self.Value(self.main_[person][main])):
                    print("    - ", main)
            for desert in deserts:
                if (self.Value(self.desert_[person][desert])):
                    print("    - ", desert)
            for drink in drinks:
                if (self.Value(self.drink_[person][drink])):
                    print("    - ", drink)

        print()


def main():
    model = cp_model.CpModel()

    # --------------------------------------------------------------------
    #                       Decision variables
    # --------------------------------------------------------------------

    # Add 4x4 Boolean variables corresponding to all combinations of objects
    # and attributes

    person_starters = {}
    for person in persons:
        variables = {}
        for starter in starters:
            variables[starter] = model.NewBoolVar(person + starter)
        person_starters[person] = variables

    # Combination of persons and mains
    person_mains = {}
    for person in persons:
        variables = {}
        for main in mains:
            variables[main] = model.NewBoolVar(person + main)
        person_mains[person] = variables

    # Combination of persons and deserts
    person_deserts = {}
    for person in persons:
        variables = {}
        for desert in deserts:
            variables[desert] = model.NewBoolVar(person + desert)
        person_deserts[person] = variables

    # Combination of persons and drinks
    person_drinks = {}
    for person in persons:
        variables = {}
        for drink in drinks:
            variables[drink] = model.NewBoolVar(person + drink)
        person_drinks[person] = variables

    # ------------------implicit constraints------------------------------------------------------

    ## Implicit 1.1 every person has a different property (starter, main, dessert, drink)
    for i in range(4):
        for j in range(i + 1, 4):
            for k in range(4):
                model.AddBoolOr([person_starters[persons[i]][starters[k]].Not(),
                                 person_starters[persons[j]][starters[k]].Not()])

                model.AddBoolOr([person_mains[persons[i]][mains[k]].Not(),
                                 person_mains[persons[j]][mains[k]].Not()])

                model.AddBoolOr([person_deserts[persons[i]][deserts[k]].Not(),
                                 person_deserts[persons[j]][deserts[k]].Not()])

                model.AddBoolOr([person_drinks[persons[i]][drinks[k]].Not(),
                                 person_drinks[persons[j]][drinks[k]].Not()])

    for person in persons:
        # at least one property per person
        variables = []
        for starter in starters:
            variables.append(person_starters[person][starter])
        model.AddBoolOr(variables)

        variables = []
        for main in mains:
            variables.append(person_mains[person][main])
        model.AddBoolOr(variables)

        variables = []
        for desert in deserts:
            variables.append(person_deserts[person][desert])
        model.AddBoolOr(variables)

        variables = []
        for drink in drinks:
            variables.append(person_drinks[person][drink])
        model.AddBoolOr(variables)

        # # Implicit 1.2. max one property per person
        for i in range(4):
            for j in range(i + 1, 4):
                model.AddBoolOr([
                    person_starters[person][starters[j]].Not(),
                    person_starters[person][starters[i]].Not()])
                model.AddBoolOr([
                    person_mains[person][mains[j]].Not(),
                    person_mains[person][mains[i]].Not()])
                model.AddBoolOr([
                    person_deserts[person][deserts[j]].Not(),
                    person_deserts[person][deserts[i]].Not()])
                model.AddBoolOr([
                    person_drinks[person][drinks[j]].Not(),
                    person_drinks[person][drinks[i]].Not()])

        # --------------------------------------------------------------------
        #                       Predicates(constraints)
        # --------------------------------------------------------------------

        # _______________________________ (1)_____________________________
        # The carpaccio starter is not combined with the vegan pie as the main course
        # AND the filet steak main course is not followed by ice cream as dessert. (1)
        # (¬carpaccio or ¬ vegan pie) ^ (¬ filet steak or ¬ice cream)

        # (¬carpaccio or ¬vegan pie) ∧ (¬vegan pie or ¬carpaccio)

        # constraint 1.1: (¬carpaccio or ¬ vegan pie)
        model.AddBoolOr([person_starters[person]["carpaccio"].Not(),
                         person_mains[person]["vegan pie"].Not()
                         ])

        # constraint 1.1 (inverse) : (¬vegan pie or ¬ carpaccio)
        model.AddBoolOr([person_mains[person]["vegan pie"].Not(),
                         person_starters[person]["carpaccio"].Not()
                         ])

        # (¬ filet steak or ¬ice cream) ^ (¬ice cream or ¬ filet steak)

        # constraint 1.2: (¬ filet steak or ¬ice cream)
        model.AddBoolOr([person_mains[person]["filet steak"].Not(),
                         person_deserts[person]["ice cream"].Not()
                         ])
        # constraint 1.2(inverse): (¬ice cream or ¬ filet steak)
        model.AddBoolOr([person_deserts[person]["ice cream"].Not(),
                         person_mains[person]["filet steak"].Not()
                         ])

        # As discussed in the lab
        # TO DO for constrain 2: tHEY ARE SEPERATE addboolor(pc.not())
        #                                             addboolor(os.not())
        # since in an or one of em gotta be true

        # _______________________________ (2)_____________________________
        # Emily does not have prawn cocktail or onion soup as the starter
        # AND none of the men have beer or coke to drink. (2)

        # Emily does not have prawn cocktail or onion soup as a starter
        # (neither "prawn cocktail" nor "onion soup" should be chosen as a starter for Emily)
        model.AddBoolOr([person_starters["Emily"]["prawn cocktail"].Not(),
                         person_starters["Emily"]["onion soup"].Not()])

        # its inverse
        model.AddBoolOr([person_starters["Emily"]["onion soup"].Not(),
                         person_starters["Emily"]["prawn cocktail"].Not()])

        # None of the men(James, Daniel) have beer or coke to drink

        # James does not have beer or coke to drink
        model.AddBoolOr([person_drinks["James"]["beer"].Not(), person_drinks["James"]["coke"].Not()])

        # Daniel does not have beer or coke to drink
        model.AddBoolOr([person_drinks["Daniel"]["beer"].Not(), person_drinks["Daniel"]["coke"].Not()])

        # _______________________________ (3)_____________________________
        # The person having prawn cocktail as the starter has baked mackerel as the main course
        # AND the filet steak main course works well with red wine. (3)

        # constraint 3.1: The person having prawn cocktail as the starter has baked mackerel as the main course
        model.AddBoolOr([person_starters[person]["prawn cocktail"].Not(),
                         person_mains[person]["baked mackerel"]
                         ])
        # constraint 3.1(inverse): The person having baked mackerel as the main course has prawn cocktail as the starter
        model.AddBoolOr([person_mains[person]["baked mackerel"].Not(),
                         person_starters[person]["prawn cocktail"]
                         ])

        # constraint 3.2: the filet steak main course works well with red wine.
        model.AddBoolOr([person_mains[person]["filet steak"].Not(),
                         person_drinks[person]["red wine"]
                         ])
        # constraint 3.2(inverse): red wine works well with the filet steak main course.
        model.AddBoolOr([person_drinks[person]["red wine"].Not(),
                         person_mains[person]["filet steak"]
                         ])

        # _______________________________ (4)_____________________________
        # One of the men has white wine as a drink
        # AND one of the women drinks coke. (4)

        # X xor y = (x ^ ¬y) v (¬x ^ y) = (¬x v ¬y) ^ (x v y)

        # X xor y = (x ^ ¬y) v (¬x ^ y)
        # constraint 4.0.1: exactly one of the men has white wine as a drink
        # James has white wine if and only if Daniel does not, and vice versa.

        # model.AddBoolOr([person_drinks["James"]["white wine"].Not(),
        #                  person_drinks["Daniel"]["white wine"]])
        #
        # model.AddBoolOr([person_drinks["Daniel"]["white wine"],
        #                  person_drinks["James"]["white wine"].Not()])
        #
        # # constraint 4.0.2: exactly one of the women drinks coke.
        # # Emily drinks coke if and only if Sophie does not, and vice versa.
        # model.AddBoolOr([person_drinks["Emily"]["coke"].Not(),
        #                  person_drinks["Sophie"]["coke"]])
        #
        # model.AddBoolOr([person_drinks["Sophie"]["coke"],
        #                  person_drinks["Emily"]["coke"].Not()])

        # Doing the second  X xor y = (¬x v ¬y) ^ (x v y)
        # Constraint 4.1: Exactly one of the men has white wine as a drink
        # James has white wine if and only if Daniel does not, and vice versa.
        model.AddBoolOr([person_drinks["James"]["white wine"].Not(),
                         person_drinks["Daniel"]["white wine"].Not()])
        model.AddBoolOr([person_drinks["James"]["white wine"],
                         person_drinks["Daniel"]["white wine"]])

        # Constraint 4.2: Exactly one of the women drinks coke.
        # Emily drinks coke if and only if Sophie does not, and vice versa.
        model.AddBoolOr([person_drinks["Emily"]["coke"].Not(),
                         person_drinks["Sophie"]["coke"].Not()])
        model.AddBoolOr([person_drinks["Emily"]["coke"],
                         person_drinks["Sophie"]["coke"]])

        # _______________________________ (5)_____________________________
        # The vegan pie main always comes with a mushroom tart as a starter and vice versa;
        # also, the onion soup and filet steak are always served together. (5)

        # case 5.1: of vice-versa: Vegan pie then mushroom tart
        model.AddBoolOr([person_mains[person]["vegan pie"].Not(),
                         person_starters[person]["mushroom tart"],
                         ])

        # case 5.2 of vice-versa: Mushroom tart then Vegan pie
        model.AddBoolOr([person_starters[person]["mushroom tart"].Not(),
                         person_mains[person]["vegan pie"],
                         ])

        # constraint 5.3: the onion soup and filet steak are always served together. (vice-versa)
        model.AddBoolOr([person_starters[person]["onion soup"].Not(),
                         person_mains[person]["filet steak"],
                         ])

        model.AddBoolOr([person_mains[person]["filet steak"].Not(),
                         person_starters[person]["onion soup"],
                         ])

        # _______________________________ (6)_____________________________
        # Emily orders beer as a drink or has fried chicken as the main and ice cream as
        # dessert; James orders coke as a drink or has onion soup as the starter and filet
        # steak as the main. (6)

        # Distribution of a disjunction over conjunctions x V (Y ^ Z) === (X V Y) ^ (X V Z)
        # 6.1 beer or (fried chicken and ice-cream) === (beer or fried chicken) ^ (beer or ice cream)

        # (beer or fried chicken)
        model.AddBoolOr([person_drinks["Emily"]["beer"],
                         person_mains["Emily"]["fried chicken"]])

        # (beer or ice cream)
        model.AddBoolOr([person_drinks["Emily"]["beer"],
                         person_deserts["Emily"]["ice cream"]])

        # constraint 6.2: James orders coke as drink or has onion soup as starter and filet steak as main
        # coke or (onion soup and filet steak) === (coke or onion soup) ^ (coke or filet steak)

        # (coke or onion soup)
        model.AddBoolOr([person_drinks["James"]["coke"],
                         person_starters["James"]["onion soup"]])

        #  (coke or filet steak)
        model.AddBoolOr([person_drinks["James"]["coke"],
                         person_mains["James"]["filet steak"]])

        # _______________________________ (7)_____________________________
        # Sophie orders chocolate cake but does not drink beer nor like fried chicken;
        # Daniel orders apple crumble for dessert but has neither carpaccio nor
        # mushroom tart as a starter. (7)

        # constraint 7.1: Sophie orders chocolate cake but does not drink beer nor likes fried chicken

        # # They are 4 different sentences.
        # sentence 1: Sophie orders chocolate cake
        model.AddBoolOr([person_deserts["Sophie"]["chocolate cake"]])

        # sentence 2: Sophie does not drink beer nor likes fried chicken

        # sentence 2.1: Sophie does drink beer
        model.AddBoolOr([person_drinks["Sophie"]["beer"].Not()])
        # sentence 2.2: Sophie does not like fried chicken
        model.AddBoolOr([person_mains["Sophie"]["fried chicken"].Not()])

        # sentence 3: Daniel orders apple crumble for desert
        model.AddBoolOr([person_deserts["Daniel"]["apple crumble"]])

        # sentence 4: Daniel orders neither carpaccio not mushroom tart as starter

        # sentence 4.1: Daniel does not order carpaccio
        model.AddBoolOr([person_starters["Daniel"]["carpaccio"].Not()])
        # sentence 4.2: Daniel does not order mushroom tart
        model.AddBoolOr([person_starters["Daniel"]["mushroom tart"].Not()])

    solver = cp_model.CpSolver()

    # Solve the CP-SAT model and determine the starter, main course, dessert, and drink ordered
    # by each of the diners

    status = solver.SearchForAllSolutions(
        model,
        SolutionPrinter(solver, person_starters, person_mains, person_deserts, person_drinks)
    )
    print(solver.StatusName(status))

    if solver.StatusName(status) == "OPTIMAL":
        for person in persons:
            if solver.Value(person_deserts[person]["tiramisu"]):
                print(person + " has tiramisu for dessert")


main()
