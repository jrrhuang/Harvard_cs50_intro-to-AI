import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    dict = {}
    # Append all pages to dictionary and add values assuming '1 - damping_factor' occured
    for key in corpus.keys():
        dict[key] = (1 - damping_factor)/len(corpus)
    # Assume 'damping_factor' occured: Check if no links are present on page, else proceed normally
    if not corpus[page]:
        for key in dict.keys():
            dict[key] += damping_factor/len(corpus)
    else:
        for val in corpus[page]:
            dict[val] += damping_factor/len(corpus[page])

    return dict

# print(transition_model({"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}, "1.html", DAMPING))

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = {}
    # initialize first sample
    prev_sample = {}
    for key in corpus.keys():
        prev_sample[key] = 1 / len(corpus)
        page_rank[key] = 0

    # Generate samples
    i = 0
    while i < n:
        page = random.choices(list(prev_sample.keys()), weights=list(prev_sample.values()), k=1)[0]
        page_rank[page] += 1
        prev_sample = transition_model(corpus, page, damping_factor)
        i += 1

    # Normalize page_rank distribution
    page_rank.update((key, val / n) for key, val in page_rank.items())
    return page_rank

# print(sample_pagerank({"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}, DAMPING, 100000))

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # initialize page_rank distribution
    page_rank = {}
    for key in corpus.keys():
        page_rank[key] = 1 / len(corpus)

    # Check if a page has no links and update it
    for key in corpus.keys():
        if not corpus[key]:
            corpus[key] = set(corpus.keys())

    # Iterate until page_rank distribution converges
    error = True
    while error:
        prev_rank = copy.deepcopy(page_rank)
        for key in page_rank.keys():
            damping_val = 0
            for page in corpus.keys():
                if key in corpus[page]:
                    damping_val += prev_rank[page] / len(corpus[page])
            page_rank[key] = (1 - damping_factor) / len(corpus) + damping_factor * damping_val
        error = check_difference(prev_rank, page_rank)
        # print(prev_rank, page_rank)
    # print(corpus)
    return page_rank

def check_difference(prev, curr):
    for key in prev.keys():
        if abs(prev[key] - curr[key]) >= 0.001:
            return True
    return False

# print(iterate_pagerank({'python.html': {'ai.html', 'programming.html'}, 'c.html': {'programming.html'}, 'logic.html': {'inference.html'}, 'programming.html': {'c.html', 'python.html'}, 'inference.html': {'ai.html'}, 'algorithms.html': {'recursion.html', 'programming.html'}, 'recursion.html': set(), 'ai.html': {'algorithms.html', 'inference.html'}}, DAMPING))
if __name__ == "__main__":
    main()
