from collections import defaultdict

import numpy as np
import json


class TransitionMatrix(defaultdict):

    def __init__(self, order):
        super().__init__(lambda: defaultdict(int))
        self.order = order

    def __repr__(self):
        return '\n'.join(f'{k} => {v}' for k, v in self.items())

    def to_serializable_dict(self):
        return {','.join(k): v for k, v in self.items()}

    def filter_values(self, values):
        """
        Filter a transition matrix, removing all the transitions towards suffixes that are not in the given list of
        values.
        If values is None, do nothing
        :param self: the matrix to filter
        :param values: the list of suffix values to keep.
        :return: the filtered matrix
        """
        if values is None:
            return self
        filtered_matrix = TransitionMatrix(self.order)
        for prefix, probabilities in self.items():
            filtered_probabilities = {suffix: probabilities[suffix] for suffix in probabilities if suffix in values}
            if filtered_probabilities:
                filtered_matrix[prefix] = filtered_probabilities
        return filtered_matrix

    def get_alphas(self):
        """
        Get the matrix alpha coefficients, i.e. the coefficient needed to normalize the matrix and make it ergodic
        :param self: the matrix where the alphas are computed
        :return: the normalization coefficients alphas
        """
        return {prefix: sum(probabilities.values()) for prefix, probabilities in self.items()}

    def normalize(self, alphas=None):
        """
        Normalize a transition matrix, by multiplying each row by its normalization coefficient alpha
        :param self: the matrix to normalize
        :param alphas: the normalization coefficients. If None, computed them on the fly. None by default
        :return: the normalized matrix
        """
        if alphas is None:
            alphas = self.get_alphas()
        res = TransitionMatrix(self.order)
        for prefix, probabilities in self.items():
            alpha = alphas[prefix]
            res[prefix] = {suffix: value / alpha for suffix, value in probabilities.items()}
        return res

    def propagate_alphas(self, alphas):
        """
        Back propagate the alpha normalization coefficients to a transition matrix. If the alphas is None, do not modify
         the input matrix
        :param self: the matrix to where back propagate the alphas
        :param alphas: the normalization coefficients to back propagate
        :return: the modified matrix
        """

        if alphas is None:
            return self
        res = TransitionMatrix(self.order)
        for prefix, probabilities in self.items():
            transitions = {}
            for suffix, value in probabilities.items():
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
    matrix = TransitionMatrix(order)
    for seq in sequences:
        for n_gram in zip(*(seq[i:] for i in range(order + 1))):
            prefix = n_gram[:-1]
            suffix = n_gram[-1]
            matrix[prefix][suffix] += 1.0
    return matrix.normalize()


def parse_sequences(sequences, max_order):
    """
    Estimate a series of transition matrices with order from O to max_order
    :param sequences: the sequences to parse to estimate the transition matrix
    :param max_order: The maximum order
    :return: The list of transition matrices, sorted by their orders
    """
    return [get_transition_matrix(sequences, order) for order in range(max_order + 1)]


class MarkovProcess:

    def __init__(self, matrices, constraints):
        """
        Create a constrained markov process that has the same distribution that the process defined by the given
         transition matrix and prior probabilities and that satisfy the given unary constraints
        :param matrices: The transition matrices describing the original markov process. The n-th element in the list
         corresponds to a transition matrix of order n
        :param constraints: The list of unary constraints. If an element in this list is None, implies no constraint to
         apply
        """
        alphas = None
        max_order = len(matrices) - 1
        self.matrices = []
        for index, values in reversed(list(enumerate(constraints))):
            # get the smaller order matrices on the beginning of the constraints
            matrix = matrices[min(index, max_order)]
            filtered = matrix.filter_values(values).propagate_alphas(alphas)
            if not filtered:
                raise RuntimeError('The constraints satisfaction problem has no solution. '
                                   'Try to relax your constraints')
            alphas = filtered.get_alphas()
            # since the loop is going back, the current transition matrix should be prepended
            self.matrices.insert(0, filtered.normalize(alphas))

    def serialize_process(self, file_path=None):
        """
        Serialize a markov process to json
        :param file_path: the path of the file where the process will be serialized. If None, the serialized json is
            returned as string by this method
        :return: the string containing the json serialized process if file_path is None. None otherwise
        """
        obj = [matrix.to_serializable_dict() for matrix in self.matrices]
        if file_path is None:
            return json.dumps(obj)
        with open(file_path, 'w') as f:
            json.dump(obj, f)

    def generate(self):
        """
        Generate a sequence according to the transition matrices and the prior probabilities
        :return: the sequence
        """
        sequence = []
        for index, matrix in enumerate(self.matrices):
            prefix = tuple(sequence[-min(index, matrix.order):])
            probabilities = matrix[prefix]
            value = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))
            sequence.append(value)
        return sequence


if __name__ == '__main__':
    c = [['C'], None, None, ['D']]
    # c = [None, None, None, ['D']]

    corpus = ['ECDECC', 'CCEEDC']
    n = 2
    ms = parse_sequences(corpus, max_order=n)
    for m in ms:
        print(m)
        print()
    print('-' * 80)
    mc = MarkovProcess(ms, c)
    for m in mc.matrices:
        print(m)
        print()
    for i in range(10):
        print(mc.generate())
    print(mc.serialize_process())
