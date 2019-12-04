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
        for i in range(len(seq) - self.order):
            prefix = self.get_symbol(tuple(seq[i: i + self.order]))
            suffix = self.get_symbol(tuple(seq[i + 1: i + self.order + 1]))
            self.transitions[prefix][suffix] += 1

    def get_transitions(self):
        return [(a1, a2) for a1, d in self.transitions.items() for a2 in d.keys()]

    def __repr__(self):
        s = ''
        for k, v in self.transitions.items():
            s += '{:} {:}\n'.format(k, dict(v))
        return s


class MarkovAutomaton():

    def __init__(self, transitions):
        self.initial_state = MarkovState()
        self.states = [self.initial_state]
        self.delta = defaultdict(dict)
        self.initial_state.final = True
        self.transitions = transitions

    def create(self):
        q = MarkovState()
        self.states.append(q)
        for a in self.transitions.alphabet.values():
            self.delta[self.initial_state][a] = q
            a.state = q
            q.incoming.append(a)
        q.final = True

        for a1, a2 in self.transitions.get_transitions()[:3]:
            print(a1, a2)
            q1 = a1.state
            q = self.separate(q1, a1)
            q2 = a2.state
            self.delta[q][a2] = q2

            # for qi, links in self.delta.items():
            #     if qi is not q and links == self.delta[q]:
            #         a1.state = qi
            #         qi.incoming += q.incoming
            #         print qi, q

            #     if exists q' in Q such that q and q' are equivalent then
            #         Merge q with q'
            #         Q(a1) <- q'; a(q') <- a(q') U a(q)

    def separate(self, q1, a1):
        q = MarkovState()
        self.states.append(q)
        q.final = True
        for a in self.transitions.alphabet.values():
            if a in self.delta[q1]:
                self.delta[q][a] = self.delta[q1][a]

        for qi, links in self.delta.items():
            if links.get(a1) is q1:
                self.delta[qi][a1] = q
        a1.state = q
        q.incoming.append(a1)
        return q

    def __repr__(self):
        s = ''
        names = {}
        for i, q in enumerate(self.states):
            name = 'q' + str(i)
            if q.final:
                name = '[' + name + ']'
            names[q] = name
        for from_state, links in self.delta.items():
            for symbol, to_state in links.items():
                s += '{:} -{:}-> {:}\n'.format(names[from_state], symbol, names[to_state])
        return s


if __name__ == '__main__':
    mt = MarkovTransitions(1)
    mt.parse('abracadabra')
    # print mt
    # for a1, a2 in mt.get_transitions():
    #     print a1, a2
    ma = MarkovAutomaton(mt)
    ma.create()
    print(ma)
