from markovconstraints.markov_chain import parse_sequences
from collections import defaultdict
from math import floor
from random import choice

# todo: Add order > 1 (if possible)
# todo: Add normalization (if possible)


class MeterConstraint:

    def __init__(self, sequences, cost, predicate, length, order=1, compute_cost_sets=True):
        self.matrices = parse_sequences(sequences, max_order=order)
        self.order = order
        self.alphabet = list(self.matrices[0][()])
        self.cost = cost
        self._predicate = predicate
        self.length = length
        self.cost_set = [defaultdict(set) for _ in range(self.length)]
        if compute_cost_sets:
            self.compute_cost_set()

    def check_predicate(self, current_cost, sequence, current_position):
        try:
            enumerator = enumerate(sequence)
        except TypeError:
            enumerator = enumerate([sequence])
        for i, element in enumerator:
            c = self.cost(element)
            if not self._predicate(current_cost, c, current_position + i):
                return False
            current_cost += c
        return True

    def compute_cost_set(self):

        # init low order cost:
        for k in range(self.order):
            # skipping the prior vector, since it is not properly a transition matrix
            matrix = self.matrices[k+1]
            for prefix in matrix:
                if self.check_predicate(0, prefix, 0):
                    self.cost_set[k][prefix].add(sum(self.cost(x) for x in prefix))

        for k in range(self.order, self.length):
            matrix = self.matrices[self.order]
            for prefix in matrix:
                for current_cost in self.cost_set[k-1][prefix]:
                    for suffix in matrix[prefix]:
                        if self.check_predicate(current_cost, suffix, k):
                            self.cost_set[k][prefix[1:] + (suffix,)].add(current_cost + self.cost(suffix))

        for k in reversed(range(self.length - 1)):
            order = min(k+1, self.order)
            matrix = self.matrices[order]
            for prefix in self.cost_set[k]:
                cost_set = set()
                for suffix in matrix[prefix]:
                    if order < self.order:
                        index = prefix + (suffix,)
                    else:
                        index = prefix[1:] + (suffix,)

                    # This is needed to avoid to create sets only by lookup
                    if index not in self.cost_set[k+1]:
                        continue
                    for cost in self.cost_set[k+1][index]:
                        previous_cost = cost - self.cost(suffix)
                        if self.check_predicate(previous_cost, suffix, k+1):
                            cost_set.add(previous_cost)
                self.cost_set[k][prefix] = self.cost_set[k][prefix].intersection(cost_set)

    def generate_next(self, prefix, order, k, c):
        elements = []
        suffixes = self.matrices[order][prefix]
        for suffix in suffixes:
            if order < self.order:
                index = prefix + (suffix,)
            else:
                index = prefix[1:] + (suffix,)
            if c + self.cost(suffix) in self.cost_set[k + 1][index]:
                elements.append(suffix)
        return choice(elements)

    def generate(self):
        sequence = []
        c = 0
        priors = [x for x, values in self.cost_set[0].items() if values]
        e = choice(priors)[0]
        sequence.append(e)
        c += self.cost(e)
        for k in range(self.length-1):
            order = min(k+1, self.order)
            prefix = tuple(sequence[-order:])
            e = self.generate_next(prefix, order, k, c)
            sequence.append(e)
            c += self.cost(e)
        return sequence


if __name__ == '__main__':

    def pred(c, x, k):
        c1 = c + x
        if k+1 == 18 and c1 != 18:
            return False
        if c % 6 != 0 and c1 % 6 != 0 and floor(c1/6) != floor(c/6):
            return False
        return True

    seq = [[1, 2, 3, 4, 3, 2, 1, 0, 0, 0], [1, 2, 4, 2, 4, 2, 0, 0]]

    # seq = [[2, 2, 2, 1, 2, 3, 1, 1, 2, 1, 1, 0, 0, 0]]

    mc = MeterConstraint(seq, int, pred, 18, order=2)
    print(mc.generate())
