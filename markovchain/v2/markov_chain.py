from collections import defaultdict

import numpy as np
import pandas as pd


class TransitionMatrix(defaultdict):

    def __init__(self, order):
        super(TransitionMatrix, self).__init__(lambda: defaultdict(int))
        self.order = order

    def __repr__(self):
        if self.order > 0:
            return str(pd.DataFrame.from_dict(self).transpose())
        return str(pd.DataFrame(data=self[()], index=['<s>']))


def filter_values(matrix, values):
    """
    Filter a transition matrix, removing all the transitions towards suffixes that are not in the given list of values
    If values is None, do nothing
    :param matrix: the matrix to filter
    :param values: the list of suffix values to keep.
    :return: the filtered matrix
    """
    if values is None:
        return matrix
    res = TransitionMatrix(order=matrix.order)
    for prefix, probabilities in matrix.items():
        filtered = {suffix: probabilities[suffix] for suffix in probabilities if suffix in values}
        if filtered:
            res[prefix] = filtered
    return res


def get_alphas(matrix):
    """
    Get the matrix alpha coefficients, i.e. the coefficient needed to normalize the matrix and make it ergodic
    :param matrix: the matrix where the alphas are computed
    :return: the normalization coefficients alphas
    """
    return {prefix: sum(probabilities.values()) for prefix, probabilities in matrix.items()}


def normalize_values(values, alpha):
    return {suffix: value / alpha for suffix, value in values.items()}


def normalize(matrix, alphas=None):
    """
    Normalize a transition matrix, by multiplying each row by its normalization coefficient alpha
    :param matrix: the matrix to normalize
    :param alphas: the normalization coefficients. If None, computed them on the fly. None by default
    :return: the normalized matrix
    """
    if alphas is None:
        alphas = get_alphas(matrix)
    res = TransitionMatrix(matrix.order)
    for prefix, probabilities in matrix.items():
        res[prefix] = normalize_values(probabilities, alphas[prefix])
    return res


def propagate_alphas(matrix, alphas):
    """
    Back propagate the alpha normalization coefficients to a transition matrix. If the alphas is None, do not modify
     the input matrix
    :param matrix: the matrix to where back propagate the alphas
    :param alphas: the normalization coefficients to back propagate
    :return: the modified matrix
    """

    if alphas is None:
        return matrix

    res = TransitionMatrix(matrix.order)
    for prefix, probabilities in matrix.iteritems():
        transitions = {}
        for suffix, value in probabilities.iteritems():
            try:
                index = prefix[1:] + (suffix,)
                transitions[suffix] = value * alphas[index]
            except KeyError:
                # Back propagating to a smaller order, try to use the whole prefix as index
                try:
                    index = prefix + (suffix,)
                    transitions[suffix] = value * alphas[index]
                except KeyError:
                    pass
        if transitions:
            res[prefix] = transitions
    return res


def get_transition_matrix(sequences, order=1):
    """
    Estimate a transition matrix from a list of sequences
    :param sequences: the sequences to parse to estimate the transition matrix
    :param order: the order of the matrix, i.e. the length of the prefix
    :return: A transition matrix
    """
    m = TransitionMatrix(order)
    for seq in sequences:
        for n_gram in zip(*(seq[i:] for i in xrange(order + 1))):
            prefix = n_gram[:-1]
            suffix = n_gram[-1]
            m[prefix][suffix] += 1.0
    return normalize(m)


def parse_sequences(sequences, max_order):
    """
    Estimate a series of transition matrices with order from O to max_order
    :param sequences: the sequences to parse to estimate the transition matrix
    :param max_order: The maximum order
    :return: The list of transition matrices, sorted by their orders
    """
    return [get_transition_matrix(sequences, order) for order in xrange(max_order + 1)]


def get_markov_process(matrices, constraints):
    """
    Compute a constrained markov process that has the same distribution that the process defined by the given
     transition matrix and prior probabilities and that satisfy the given unary constraints
    :param matrices: The transition matrices describing the original markov process. The n-th element in the list
     corresponds to a transition matrix of order n
    :param constraints: The list of unary constraints. If an element in this list is None, implies no constraint to
     apply
    """
    alphas = None
    max_order = len(matrices) - 1
    markov_process = []
    for index, values in reversed(list(enumerate(constraints))):
        matrix = matrices[min(index, max_order)]  # get the smaller order matrices on the beginning of the constraints
        filtered = filter_values(matrix, values)
        filtered = propagate_alphas(filtered, alphas)
        if not filtered:
            raise RuntimeError('The constraints satisfaction problem has no solution. '
                               'Try to relax your constraints')
        alphas = get_alphas(filtered)
        # since the loop is going back, the current transition matrix should be prepended
        markov_process.insert(0, normalize(filtered, alphas))
    return markov_process


def generate(markov_process):
    """
    Generate a sequence according to the transition matrices and the prior probabilities
    :return: the sequence
    """
    sequence = []
    for i, m in enumerate(markov_process):
        prefix = tuple(sequence[-min(i, m.order):])
        probabilities = m[prefix]
        value = np.random.choice(probabilities.keys(), p=probabilities.values())
        sequence.append(value)
    return sequence


if __name__ == '__main__':
    c = [['C'], None, None, ['D']]
    c = [None, None, None, ['D']]

    corpus = ['ECDECC', 'CCEEDC']
    n = 2
    ms = parse_sequences(corpus, max_order=n)
    for m in ms:
        print m
    mc = get_markov_process(ms, c)
    for m in mc:
        print m
    for i in xrange(10):
        print generate(mc)
