__author__ = 'gabrielebarbieri'
from collections import defaultdict

# A = <Q, E, d, q0, F >, where:


class MarkovSymbol():

    def __init__(self, value):
        self.value = value
        self.state = None

    def __repr__(self):
        return str(self.value)


class MarkovState():

    def __init__(self):
        self.incoming = []
        self.final = False


class MarkovTransitions():

    def __init__(self, order):
        self.order = order
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.alphabet = {}

    def get_symbol(self, value):
        return self.alphabet.setdefault(value, MarkovSymbol(value))

    def parse(self, seq):
        for i in xrange(len(seq) - self.order):
            prefix = self.get_symbol(tuple(seq[i: i + self.order]))
            suffix = self.get_symbol(tuple(seq[i + 1: i + self.order + 1]))
            self.transitions[prefix][suffix] += 1


class MarkovAutomaton():

    def __init__(self):
        self.initial_state = MarkovState()
        self.states = [self.initial_state]
        self.delta = defaultdict(dict)
        self.initial_state.final = True

    def create(self, transitions):
        q = MarkovState()
        self.states.append(q)
        for a in transitions.alphabet.values():
            self.delta[self.initial_state][a] = q
            a.state = q
            q.incoming.append(a)
        self.final_states.append(q)
        # for all the a ∈ Σ do
        #     δ(q0,a) ← q
        #     Q(a) ← q; a(q) ← a(q) ∪ {a}
        #     F←F∪{q0,q}

        pass

if __name__ == '__main__':
    mt = MarkovTransitions(1)
    mt.parse('abracadabra')
    for k, v in mt.transitions.items():
        print k, dict(v)