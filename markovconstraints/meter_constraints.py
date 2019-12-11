from markovconstraints.markov_chain import parse_sequences
from collections import defaultdict
from math import floor
from random import choice

# todo: Add order > 1 (if possible)
# todo: Add normalization (if possible)


class MeterConstraint:

    def __init__(self, sequences, cost, predicate, length, order=1, compute_cost_sets=True):
        self.matrices = parse_sequences(sequences, max_order=order)
        self.alphabet = list(self.matrices[0][()])
        self.cost = cost
        self._predicate = predicate
        self.length = length
        self.cost_set = defaultdict(set)
        if compute_cost_sets:
            self.compute_cost_set()

    def predicate(self, c, y, k):
        return self._predicate(c, self.cost(y), k)

    def compute_cost_set(self):
        matrix = self.matrices[1]
        for x in self.alphabet:
            k = 0
            if self.predicate(0, x, k):
                self.cost_set[(x, k)].add(self.cost(x))
        for k in range(self.length - 1):
            for x in self.alphabet:
                for y in matrix[(x,)]:
                    for c in self.cost_set[(x, k)]:
                        if self.predicate(c, y, k+1):
                            self.cost_set[(y, k+1)].add(c + self.cost(y))
        for k in reversed(range(self.length - 1)):
            for x in self.alphabet:
                cost_set = set()
                for y in matrix[(x,)]:
                    for c in self.cost_set[(y, k+1)]:
                        if self.predicate(c - self.cost(y), y, k+1):
                            cost_set.add(c - self.cost(y))
                self.cost_set[(x, k)] = self.cost_set[(x, k)].intersection(cost_set)

    def generate_next(self, prefix, k, c):
        max_order = len(prefix)
        for i in range(len(prefix)):
            order = max_order - i
            print(order)
            elements = [y for y in self.matrices[order][prefix[i:]] if c + self.cost(y) in self.cost_set[(y, k+1)]]
            if elements:
                return choice(elements)

    def generate(self):
        sequence = []
        c = 0
        priors = [x for x in self.alphabet if self.cost_set[(x, 0)]]
        e = choice(priors)
        sequence.append(e)
        c += self.cost(e)
        for k in range(self.length-1):
            prefix = tuple(sequence[-min(k, len(self.matrices)-1):])
            e = self.generate_next(prefix, k, c)
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

    seq = [[1, 2, 3, 4, 3, 2, 1, 0, 0], [1, 2, 4, 2, 1, 0]]

    g = MeterConstraint(seq, int, pred, 18, order=3)
    # print(g.matrix)
    print(g.generate())
