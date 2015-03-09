__author__ = 'gabrielebarbieri'

from collections import defaultdict
import random


class MarkovProcess():

    def __init__(self, order):
        self.order = order
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.transposed = defaultdict(lambda: defaultdict(int))

    def parse(self, sequence):
        for k in xrange(self.order + 1):
            for i in xrange(len(sequence) - k):
                self._parse_sub_sequence(sequence[i:i+k+1])

    def _parse_sub_sequence(self, seq):
        prefix = tuple(seq[:-1])
        e = seq[-1]
        self.transitions[prefix][e] += 1
        if len(prefix) is self.order:
            self.transposed[e][prefix] += 1

    def __repr__(self):
        rep = ''
        for k in xrange(self.order + 1):
            for prefix, trans in self.transitions.items():
                if len(prefix) is k:
                    rep += str(prefix) + ': ' + str(dict(trans)) + '\n'
        return rep[:-1]

    def generate_item(self, prefix, allowed):
        """
        Generate a new items drawing from the allowed item according to the node probabilities
        Note: does not work if allowed contains duplicated items
        For more details see: http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python
        """
        total = 0
        weights = {}
        frequencies = self.transitions[prefix]
        for v in allowed:
            if v in frequencies:
                p = frequencies[v]
                weights[v] = p
                total += p
        rnd = random.random() * total
        for k, w in weights.items():
            rnd -= w
            if rnd < 0:
                return k

if __name__ == '__main__':
    s = 'mississipix'
    mt = MarkovProcess(2)
    mt.parse(s)
    # print mt
    res = defaultdict(int)
    for l in xrange(100):
        res[mt.generate_item(tuple('i'), ['s', 'x'])] += 1
    print dict(res)