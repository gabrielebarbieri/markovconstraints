__author__ = 'gabrielebarbieri'

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


class MarkovAutomaton():

    def __init__(self):
        self.states = []  # Q is a finite non-empty set of states
        self.alphabet = {}  # E is the alphabet - a finite non-empty set of symbols;
        self.initial_state = None  # q0 in Q is the initial state of the automaton;
        self.transitions = {}  # d is the transition function Q x E -> Q;
        self.final_states = []  # F in Q is the set of final, or accepting, states.
