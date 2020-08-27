from nltk import *
import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until" | "but" | "or"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP Conj S | NP VP Conj VP
AP -> Adj | Adj AP
NP -> N | Det NP | AP NP | N PP
PP -> P NP
VP -> V | V NP | V NP PP | V PP | Adv VP | VP Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    word_lst = [token.lower() for token in nltk.tokenize.word_tokenize(sentence)
                if re.search('[a-zA-Z]', token)]
    return word_lst

#print(preprocess("He wants p-P to eat peanuts."))
def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    '''# Return empty if terminal, else return list of children.
    if check_terminal(tree):
        return []
    else:
        children = list(tree)

    np_chunks = []
    # Add to np_chunks if no 'NP' in subtrees, else call recursion to get any further np_chunks.
    for child in children:
        if child.label() == 'NP' and check_subtrees(child):
            np_chunks.append(child)
        else:
            np_chunks += np_chunk(child)'''

    np_chunks = [t for t in tree.subtrees() if t.label() == 'NP' and check_subtrees(t)]
    return np_chunks

def check_terminal(tree):
    if tree.label() in ['Adj', 'Adv', 'Conj', 'Det', 'N', 'P', 'V']:
        return True
    return False

def check_subtrees(tree):
    i = 0
    for s in tree.subtrees():
        if i != 0:
            if s.label() == 'NP':
                return False
        i += 1
    return True

if __name__ == "__main__":
    main()
