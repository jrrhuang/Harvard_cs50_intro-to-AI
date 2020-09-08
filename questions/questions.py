from nltk import *
import nltk
import sys
import os
import string
import math
#nltk.download('stopwords')

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    text_dict = {}
    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        with open(path) as text:
            text_dict[entry] = text.read()

    return text_dict
# print(load_files('/Users/jerryhuang/Downloads/questions/corpus/'))

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    word_lst = [token.lower() for token in nltk.word_tokenize(document)
                if token not in string.punctuation and token.lower() not in nltk.corpus.stopwords.words("english")]
    return word_lst

#print(tokenize(load_files('/Users/jerryhuang/Downloads/questions/corpus/')['python.txt']))
def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Obtain set of words across all docs
    words = set()
    for filename in documents:
        words.update(documents[filename])

    # Calculate idfs
    idfs = dict()
    for word in words:
        val = sum(word in documents[filename] for filename in documents)
        idfs[word] = math.log(len(documents) / val)

    return idfs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    files_tfidf = []
    # loop through files and words in query
    # calc sum of all tf-idfs for query words in file
    for file in files:
        tfidf = 0
        for word in query:
            tf = files[file].count(word)
            tfidf += tf * idfs[word]
        files_tfidf.append((file, tfidf))
    sorted_files = sorted(files_tfidf, key=lambda x: x[1], reverse=True)[:n]

    return [i[0] for i in sorted_files]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentences_idf = []
    for sentence in sentences:
        # Calc total idf in sentence
        s_tokens = sentences[sentence]
        idf = sum(idfs[word] for word in query
                  if word in s_tokens)

        # Calc query term density in sentence
        qtd = sum(word in query for word in s_tokens) / len(s_tokens)
        sentences_idf.append((sentence, idf, qtd))

    sorted_sentences = sorted(sentences_idf, key=lambda x: (x[1], x[2]), reverse=True)[:n]

    return [i[0] for i in sorted_sentences]

if __name__ == "__main__":
    main()
