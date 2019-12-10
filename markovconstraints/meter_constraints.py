from markovconstraints.markov_chain import get_transition_matrix, TransitionMatrix
from collections import defaultdict
from math import floor
from random import choice

# todo: Add order > 1 (if possible)
# todo: Add normalization (if possible)


class MeterConstraint:

    def __init__(self, sequences, cost, predicate, length, compute_cost_sets=True):
        self.matrix = TransitionMatrix(1)
        for x, value in get_transition_matrix(sequences).items():
            self.matrix[x[0]] = value
        self.alphabet = sorted([e for e in self.matrix.keys()])
        self.cost = cost
        self._predicate = predicate
        self.length = length
        self.cost_set = defaultdict(set)
        if compute_cost_sets:
            self.compute_cost_set()

    def predicate(self, c, y, k):
        return self._predicate(c, self.cost(y), k)

    def compute_cost_set(self):
        for x in self.alphabet:
            k = 0
            if self.predicate(0, x, k):
                self.cost_set[(x, k)].add(self.cost(x))
        for k in range(self.length - 1):
            for x in self.alphabet:
                for y in self.matrix[x]:
                    for c in self.cost_set[(x, k)]:
                        if self.predicate(c, y, k+1):
                            self.cost_set[(y, k+1)].add(c + self.cost(y))
        for k in reversed(range(self.length - 1)):
            for x in self.alphabet:
                cost_set = set()
                for y in self.matrix[x]:
                    for c in self.cost_set[(y, k+1)]:
                        if self.predicate(c - self.cost(y), y, k+1):
                            cost_set.add(c - self.cost(y))
                self.cost_set[(x, k)] = self.cost_set[(x, k)].intersection(cost_set)

    def generate_next(self, x, k, c):
        elements = [y for y in self.matrix[x] if c + self.cost(y) in self.cost_set[(y, k+1)]]
        return choice(elements)

    def generate(self):
        sequence = []
        c = 0
        priors = [x for x in self.alphabet if self.cost_set[(x, 0)]]
        e = choice(priors)
        sequence.append(e)
        c += self.cost(e)
        for k in range(self.length -1):
            e = self.generate_next(sequence[-1], k, c)
            sequence.append(e)
            c += self.cost(e)
        return sequence


if __name__ == '__main__':
    seq = [[1, 2, 3, 4, 3, 2, 1, 0, 0], [1, 2, 4, 2, 1, 0]]

    def pred(c, x, k):
        c1 = c + x
        if k+1 == 18 and c1 != 18:
            return False
        if c % 6 != 0 and c1 % 6 != 0 and floor(c1/6) != floor(c/6):
            return False
        return True

    g = MeterConstraint(seq, int, pred, 18)
    print(g.generate())
