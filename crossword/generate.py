import sys
import copy
from collections import deque
import random

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        '''for overlap in self.crossword.overlaps:
            if self.crossword.overlaps[overlap] is None:
                print(overlap)'''
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            var_length = var.length
            var_domain = copy.deepcopy(self.domains[var])
            for word in var_domain: # Remove words that are not the same length as var
                if len(word) != var_length:
                    self.domains[var].remove(word)

    def revise(self, x, y, assignment=None):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        if self.crossword.overlaps[(x, y)]:
            c1, c2 = self.crossword.overlaps[(x, y)]
            toRemove = set()
            # if assigned, change domain to consider
            if assignment:
                domain_y = {assignment[y]}
            else:
                domain_y = self.domains[y]
            # revise
            for word_x in self.domains[x]:
                if not any(word_x[c1] == word_y[c2] for word_y in domain_y):
                    toRemove.add(word_x)
                    revised = True

            self.domains[x] -= toRemove
        return revised

    def ac3(self, arcs=None, assignment=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs:
            while arcs:
                x, y = arcs.popleft()
                if self.revise(x, y, assignment):  # If x's domain is revised, we need to check if it is still arc consistent with other variables
                    if len(self.domains[x]) == 0:
                        return False
            self.ac3()
        else:  # if empty, add all constraining arcs in self.crossword.overlaps
            arcs = deque([arc for arc in self.crossword.overlaps if self.crossword.overlaps[arc]])

            while arcs:
                x, y = arcs.popleft()
                if self.revise(x, y): # If x's domain is revised, we need to check if it is still arc consistent with other variables
                    if len(self.domains[x]) == 0:
                        return False
                    for var in self.crossword.neighbors(x):
                        if var != y:
                            arcs.append((var, x))
                # remove duplicates
                arcs = deque(set(arcs))
        # print(self.domains)
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            # Correct length
            if len(assignment[var]) != var.length:
                return False
            # Uniqueness
            if len(set(assignment.values())) < len(assignment):
                return False
            # Overlap
            for v in self.crossword.neighbors(var):
                if v in assignment and self.crossword.overlaps[(var, v)]:
                    c1, c2 = self.crossword.overlaps[(var, v)]
                    if assignment[var][c1] != assignment[v][c2]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        lst = []
        for word in self.domains[var]:
            count = 0
            for v in self.crossword.neighbors(var):
                if v in assignment or not self.crossword.overlaps[(var, v)]:
                    continue
                c1, c2 = self.crossword.overlaps[(var, v)]
                for w in self.domains[v]:
                    if word[c1] != w[c2]:
                        count += 1
            lst.append((word, count))

        # sort
        return [i[0] for i in sorted(lst, key=lambda x: x[1])]

        # return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # lst consisting of (var, domain_size, degree)
        lst = []
        for var in self.crossword.variables - set(assignment):
            domain_size = len(self.domains[var])
            degree = len(self.crossword.neighbors(var) - set(assignment))
            lst.append((var, domain_size, degree))

        # sort by domain size and degree before returning variable
        return min(lst, key=lambda x: (x[1], -x[2]))[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Return assignment if it is complete
        if self.assignment_complete(assignment):
            return assignment

        # Start searching
        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment): # assign word to unassigned variable
            assignment[var] = val
            inferences = self.inference(var, assignment)
            if self.consistent(assignment): # If consistent, check result of new assignment
                if inferences:
                    assignment.update(inferences)
                res = self.backtrack(assignment)
                if res:
                    return res
            assignment.pop(var)
            for entry in inferences:
                if entry in assignment:
                    assignment.pop(entry)

        return None


# python reattempt.py data/structure2.txt data/words2.txt
# python re-generate.py data/structure2.txt data/words2.txt
    def inference(self, var, assignment):
        # find neighboring arcs
        neighbors = self.crossword.neighbors(var)
        arcs = deque([(x, var) for x in neighbors if x not in assignment])

        # ac3
        new_inferences = {}
        if self.ac3(arcs, assignment):
            # infer
            for v in self.domains:
                if len(self.domains[v]) == 1 and v not in assignment:
                    new_inferences[v] = list(self.domains[v])[0]

        # print(inferences)

        return new_inferences


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
