import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import GaussianNB

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        evidence = []
        labels = []
        i = 0
        for row in csv_reader:
            if i == 0:
                categories = row
                i += 1
            else:
                evidence_ele, label = curate(row, categories)
                evidence.append(evidence_ele)
                labels.append(label)
        return evidence, labels

def curate(row, categories):
    evidence_ele = []
    float_categories = ['Administrative_Duration', 'Informational_Duration', 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay']
    for i in range(len(categories)):
        if categories[i] == 'Month':
            evidence_ele.append(ret_month(row[i]))
        elif categories[i] == 'VisitorType':
            if row[i] == 'Returning_Visitor':
                evidence_ele.append(1)
            else:
                evidence_ele.append(0)
        elif categories[i] == 'Weekend':
            if row[i] == 'TRUE':
                evidence_ele.append(1)
            else:
                evidence_ele.append(0)
        elif categories[i] == 'Revenue':
            if row[i] == 'TRUE':
                label = 1
            else:
                label = 0
        elif categories[i] in float_categories:
            evidence_ele.append(float(row[i]))
        else:
            evidence_ele.append(int(row[i]))
    return evidence_ele, label

def ret_month(month):
    month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for i in range(len(month_lst)):
        if month in month_lst[i]:
            return i

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    #model = GaussianNB()
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sensitivity_count = 0
    specificity_count = 0
    pos_total = 0
    neg_total = 0
    for i in range(len(labels)):
        if labels[i] == 1:
            pos_total += 1
            if predictions[i] == 1:
                sensitivity_count += 1
        else:
            neg_total += 1
            if predictions[i] == 0:
                specificity_count += 1

    return sensitivity_count / pos_total, specificity_count / neg_total

if __name__ == "__main__":
    main()
