# -*- coding: utf-8 -*-

from collections import defaultdict
import random

__author__ = 'Gabriele'

MIN_ACCEPTED_FREQUENCY = 2


class MarkovNode:
    """
    A node in a Markov Suffix Tree
    """

    def __init__(self, value):
        self.value = value
        self.continuations = []
        self.probabilities = defaultdict(int)
        self.sons = {}
        self.tag = -1

    def add_continuation(self, c):
        """
        Add a continuation and increment its frequency
        """
        p = self.probabilities[c.value] + 1
        self.probabilities[c.value] = p
        if p == MIN_ACCEPTED_FREQUENCY:
            self.continuations.append(c)

    def get_son(self, value):
        """
        Get the son corresponding to the given value. Create it if it does not exist
        """
        try:
            return self.sons[value]
        except KeyError:
            son = MarkovNode(value)
            self.sons[value] = son
            return son

    def __repr__(self):
        return "{:} -> {:}".format(self.value, dict(self.probabilities))

    def recursive_rep(self, depth=0, father=''):
        """
        Represent the node and all its sons recursively
        """
        s = '  ' * depth
        s += "{:} -> {:}\n".format(self.value + father, dict(self.probabilities))
        for son in self.sons.values():
            s += son.recursive_rep(depth + 1, self.value + father)
        return s

    def generate_item(self, allowed):
        """
        Generate a new items drawing from the allowed item according to the node probabilities
        Note: does not work if allowed contains duplicated items
        For more details see: http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python
        """
        total = 0
        weights = {}
        for v in allowed:
            if v in self.probabilities:
                p = self.probabilities[v]
                weights[v] = p
                total += p
        rnd = random.random() * total
        for k, w in weights.items():
            rnd -= w
            if rnd < 0:
                return k

    def parse_prefix(self, prefix):
        """
        Parse the prefix sequence and create the sons accordingly. Return the created nodes
        """
        n = self
        parsed = []
        for v in reversed(prefix):
            if v:
                n = n.get_son(v)
                parsed.append(n)
        return parsed


class MarkovTree:
    """
    A suffix tree structure for representing all variable-length Markov chains of input data.
    Each data is the root of a tree structure (Node). Sons of this node represent the ancestors of the data in some
    input sequence.
    """
    def __init__(self, order=2):
        self.max_order = order
        self.alphabet = {}

    def parse(self, values):
        """
        Parse the list of value and update the tree
        """
        for i, v in enumerate(values):
            node = self.get_node(v)
            prefix = values[max(0, i - self.max_order + 1): i]
            suffix = values[i+1: i+2]
            sons = node.parse_prefix(prefix)
            if suffix:
                cont = self.get_node(suffix[0])
                node.add_continuation(cont)
                for son in sons:
                    son.add_continuation(cont)

    def get_node(self, v):
        """
        Get the root node in the tree corresponding to the given value. Create the node if it does not exist
        """
        return self.alphabet.setdefault(v, MarkovNode(v))

    def __repr__(self):
        s = ''
        for node in self.alphabet.values():
            s += node.recursive_rep()
        return s
