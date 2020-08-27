import csv
import itertools
import sys
from collections import deque

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_prob = 1
    for person in people.keys():
        if not (people[person]['mother'] or people[person]['father']): # Checks if the person doesn't have a listed mother and father
            num_genes = gene_ret(one_gene, two_genes, person)
            trait = trait_ret(have_trait, person)
            # print(PROBS["gene"][num_genes], PROBS["trait"][num_genes][trait])
            joint_prob *= PROBS["gene"][num_genes] * PROBS["trait"][num_genes][trait]
        else: # casework for person that has listed mother and father
            child_gene = gene_ret(one_gene, two_genes, person)
            child_trait = trait_ret(have_trait, person)
            mother_gene = gene_ret(one_gene, two_genes, people[person]['mother'])
            father_gene = gene_ret(one_gene, two_genes, people[person]['father'])

            # List of ways to constitute child_gene as pair (mother, father)
            inheritance = []
            for i in range(child_gene + 1):
                if i <= 1 and child_gene - i <= 1:
                    inheritance.append((i, child_gene - i))

            # Calculate total_prob for genes
            total_prob = 0
            for pair in inheritance:
                total_prob += calc_indiv_case_genes(mother_gene, pair[0]) * calc_indiv_case_genes(father_gene, pair[1])

            # Calculate joint_prob
            joint_prob *= total_prob * PROBS["trait"][child_gene][child_trait]

    return joint_prob


def calc_indiv_case_genes(num_genes, target_gene):
    mutation_rate = PROBS["mutation"]
    if target_gene == 0:
        prob = num_genes / 2 * mutation_rate + (1 - num_genes / 2) * (1 - mutation_rate)
    else:
        prob = num_genes / 2 * (1 - mutation_rate) + (1 - num_genes / 2) * mutation_rate
    return prob

# Return the number of genes for the person we are calculating the probability for
def gene_ret(one_gene, two_genes, person):
    if person in one_gene:
        return 1
    if person in two_genes:
        return 2
    return 0

# Return whether the person has the trait or not
def trait_ret(have_trait, person):
    if person in have_trait:
        return True
    return False

'''people = {
  'Harry': {'name': 'Harry', 'mother': 'Lily', 'father': 'James', 'trait': None},
  'James': {'name': 'James', 'mother': None, 'father': None, 'trait': True},
  'Lily': {'name': 'Lily', 'mother': None, 'father': None, 'trait': False}
}'''
# print(joint_probability(people, {"Harry"}, {"James"}, {"James"}))

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        num_genes = gene_ret(one_gene, two_genes, person)
        trait = trait_ret(have_trait, person)
        probabilities[person]["gene"][num_genes] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities.keys():
        for distribution in probabilities[person].keys():
            total = sum(probabilities[person][distribution].values())
            probabilities[person][distribution] = {key: val / total for key, val in probabilities[person][distribution].items()}

'''probabilities = {
        'dude': {
            "gene": {
                2: .25,
                1: .25,
                0: .25
            },
            "trait": {
                True: .1,
                False: .3
            }
        }
    }
normalize(probabilities)
print(probabilities)'''
if __name__ == "__main__":
    main()

