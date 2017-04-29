import numpy as np
from collections import defaultdict


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
    res = {}
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


def normalize(matrix, alphas=None):
    """
    Normalize a transition matrix, by multiplying each row by its normalization coefficient alpha
    :param matrix: the matrix to normalize
    :param alphas: the normalization coefficients. If None, computed them on the fly. None by default
    :return: the normalized matrix
    """
    if alphas is None:
        alphas = get_alphas(matrix)

    return {prefix: {suffix: value / alphas[prefix] for suffix, value in probabilities.items()}
            for prefix, probabilities in matrix.items()}


def propagate_alphas(matrix, alphas):
    """
    Back propagate the alpha normalization coefficients to a transition matrix. If the alphas is None, do not modify
     the input matrix
    :param matrix: the matrix to where back propagate the alphas
    :param alphas: the normalization coefficients to back propagate
    :return: the modified matrix
    """

    # TODO: manage order > 1
    if alphas is None:
        return matrix

    res = {}
    for prefix, probabilities in matrix.iteritems():
        tr = {}
        for suffix, value in probabilities.iteritems():
            try:
                tr[suffix] = value * alphas[tuple(suffix)]
            except KeyError:
                pass
        if tr:
            res[prefix] = tr
    return res


def get_transition_matrix(sequences, order=1):
    m = defaultdict(lambda: defaultdict(int))
    for seq in sequences:
        for n_gram in zip(*(seq[i:] for i in xrange(order + 1))):
            prefix = n_gram[:-1]
            suffix = n_gram[-1]
            m[prefix][suffix] += 1.0
    return normalize(m)


def get_prior_probabilities(sequences):
    priors = defaultdict(int)
    tot = 0
    for seq in sequences:
        tot += len(seq)
        for value in seq:
            priors[value] += 1.0
    return {k: v / tot for (k, v) in priors.items()}


class MarkovChain(object):

    def __init__(self, matrix, priors, constraints):
        """
        Compute a constrained markov process that has the same distribution that the process defined by the given
         transition matrix and prior probabilities and that satisfy the given unary constraints
        :param matrix: The transition matrix describing the original markov process
        :param priors: The prior probabilities
        :param constraints: The list of unary constraints. If an element in this list is None, implies no constraint to
         apply
        """
        alphas = None
        self.matrices = []
        for values in reversed(constraints[1:]):
            filtered = filter_values(matrix, values)
            filtered = propagate_alphas(filtered, alphas)
            if not filtered:
                raise RuntimeError('The constraints satisfaction problem has no solution. '
                                   'Try to relax your constraints')
            alphas = get_alphas(filtered)
            # since the loop is going back, the current transition matrix should be prepended
            self.matrices.insert(0, normalize(filtered, alphas))

        if constraints[0] is not None:
            f = {k: v for k, v in priors.items() if k in constraints[0]}
        else:
            f = priors
        print f
        f = {k: v * alphas[tuple(k)] for k, v in f.items() if tuple(k) in alphas}
        alpha = sum(f.values())
        self.priors = {k: v / alpha for (k, v) in f.items()}

    def generate(self):
        """
        Generate a sequence according to the transition matrices and the prior probabilities
        :return: the sequence
        """
        probabilities = self.priors
        value = np.random.choice(probabilities.keys(), p=probabilities.values())
        sequence = [value]
        for m in self.matrices:
            # TODO: manage higher order (the tuple here is a hack)
            probabilities = m[tuple(value)]
            value = np.random.choice(probabilities.keys(), p=probabilities.values())
            sequence.append(value)
        return sequence

if __name__ == '__main__':

    c = [['C'], None, None, ['D']]

    corpus = ['ECDECC', 'CCEEDC']
    M = get_transition_matrix(corpus)
    p = get_prior_probabilities(corpus)
    mc = MarkovChain(M, p, c)
    for i in xrange(10):
        print mc.generate()

