import os
"""
CMPSC 464 Project 2 - CFGs, CNFs, and Feasibility
Implemented by Gabriel Kaim, Henry Kopp, and Colin Ruark
Add the file to cfg.txt and input your string when prompted for information about the test case
"""

def parse_grammar(filename):
    """
    Takes in a file, splits it up by line and OR component
    Uses this information to populate a dictionary with:
    - Key: Left-hand side nonterminal
    - Value: List of all possible Right-hand sides
    """
    grammar = {}
    # Reading in all lines separately
    with open(filename, 'r') as f:
        lines = [line for line in f.readlines()]

    #top line doesn't really matter if we know how many lines were craffed in previous step
    for i in range(1, len(lines)):
        line = lines[i]

        # Find two halves of transition by both sides of the '='
        rule_parts = line.split('=')
        if len(rule_parts) == 2:
            nonterminal = rule_parts[0].strip()
            # Check all OR components to put them into a transition dictionary
            right_hand_sides = rule_parts[1].split('|')

            # Adds to dictionary if first non-terminal appearance
            if nonterminal not in grammar:
                grammar[nonterminal] = []
            #otherwise adds to the non-terminal dictionary
            grammar[nonterminal].extend(right_hand_sides)

    return grammar

#Checks if value is a terminal 
def is_terminal(symbol):
    return ('a' <= symbol <= 'z') or ('0' <= symbol <= '9') or symbol == '$'

#Checks if value is nonterminal
def is_nonterminal(symbol):
    return 'A' <= symbol <= 'Z'

def check_cnf_validity(filename):
    """
    Various Checks:
    - S is not repeated
    - All nonterminal -> nonterminal transitions are of the form X -> YZ
        (Where X, Y, Z are all nonterminals)
    - All nonterminal -> terminal transitions are of the form X -> x
        (Where X is nonterminal, x is terminal)
    - If epsilon exists, it must come directly from S
    """
    grammar = parse_grammar(filename)

    for nonterminal, right_hand_sides in grammar.items():
        # Checks if the left hand side is exactly one nonterminal, o.w. reject
        if not is_nonterminal(nonterminal) or len(nonterminal) != 1:
            return "no"

        for production in right_hand_sides:
            # Checks if epsilon comes from S, o.w. rejects
            if production == '$':
                if nonterminal != 'S':
                    return "no"

            # Checks that all nonterminal -> terminals are of the form X -> x
            elif len(production) == 1:
                if not is_terminal(production):
                    return "no"

            # Checks that all nonterminal -> nonterminals are of the form X -> YZ, as described in docstring
            elif len(production) == 2:
                if not (is_nonterminal(production[0]) and is_nonterminal(production[1])):
                    return "no"
                if production[0] == 'S' or production[1] == 'S':
                    return "no"

            # Anything outside of the forms provided above auto-reject
            else:
                return "no"

    # If no failing points are found, accepts
    return "yes"

def is_string_in_grammar(filename, string):
    """
    If a grammar G is in Chomsky normal form, any derivation of string w of length n≥1 in G has 2n-1 steps.
        Checks all branches of 2n-1 steps and checks if the string accepts in any branch
        Exponential Runtime (Important for later calculation)
    """
    grammar = parse_grammar(filename)

    # How does treating '$' the same as an empty string simplify the rest of the logic?
    if string == "$" or string == "":
        target = ""
        string_length = 0
    else:
        target = string
        string_length = len(string)

    # Empty strings still need one step to calculate, otherwise docstirng rule applies
    if string_length == 0:
        required_derivation_steps = 1
    else:
        required_derivation_steps = 2 * string_length - 1

    # Starting with empty stack with 0 steps taken (counts to 2n-1)
    dfs_stack = [("S", 0)]

    while dfs_stack:
        current_string, steps_taken = dfs_stack.pop()

        # When we're at 2n-1 steps and we've found the target string, accept immediately
        if steps_taken == required_derivation_steps:
            if current_string == target:
                return "yes"
            continue

        # Finds the first nonterminal for transitions
        leftmost_nonterminal_index = -1
        for i, char in enumerate(current_string):
            if is_nonterminal(char):
                leftmost_nonterminal_index = i
                break

        # If there are no nonterminals, this is a dead branch, and continues to try the next branch on the stack
        if leftmost_nonterminal_index == -1:
            continue

        # Runs all possible scenarios from the current nonterminal
        leftmost_nonterminal = current_string[leftmost_nonterminal_index]
        if leftmost_nonterminal in grammar:
            for production in grammar[leftmost_nonterminal]:
                #Adds all plausible next steps in the path to the stack to be evaluated later
                substitution = "" if production == "$" else production
                next_derivation = current_string[:leftmost_nonterminal_index] + substitution + current_string[leftmost_nonterminal_index + 1:]
                dfs_stack.append((next_derivation, steps_taken + 1))

    # If no successful branches found, return 'no'
    return "no"

def check_search_feasibility(filename, string_length):
    """
    How do the worst-case branching factor and derivation depth together determine
    whether the naive DFS in is_string_in_grammar can finish within one minute?
    """
    grammar = parse_grammar(filename)

    # For all possible transitions that can be reached during one rule, find the max
    max_branching_factor = max((len(rules) for rules in grammar.values()), default=0)

    # Calculate the number of steps in a CNF grammar
    derivation_length = 2 * string_length - 1 if string_length > 0 else 1

    # Checks the total number of branches with 2n-1 steps
    worst_case_path_count = max_branching_factor ** derivation_length

    # Arbitary value for computation threshold between 
    path_count_threshold = 10 ** 8

    if worst_case_path_count <= path_count_threshold:
        return "yes"
    else:
        return "no"

if __name__ == "__main__":
    filename = os.path.join(os.path.dirname(__file__), "cfg.txt")
    input_string = input("Enter a string: ")

    print("Is CNF?")
    print(check_cnf_validity(filename))
    print("Is in Grammar?")
    print(is_string_in_grammar(filename, input_string))
    print("Is feasible?")
    print(check_search_feasibility(filename, len(input_string)))
