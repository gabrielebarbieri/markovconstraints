__author__ = 'gabrielebarbieri'
import logging
from datetime import datetime
from markov import MarkovProcess


class Value():

    def __init__(self, value, csp_size):
        self.value = value
        self.domains = [False] * csp_size
        self.ins = [False] * csp_size
        self.outs = [{} for d in xrange(csp_size)]

    def __repr__(self):
        return str(self.value)

    def link(self, suffix, pos):
        self.outs[pos][suffix] = 1
        suffix.ins[pos + 1] = True


def accept(prefix, i):
    for k, v in enumerate(reversed(prefix)):
        j = i - k - 1
        if not v.domains[j]:
            return False
    return True


class ConstraintChain():
    """
    A Constraint Chain: two adjacent variables are constrained by a Markov Constrain.
    """

    def __init__(self, variables, order):
        self.size = len(variables)
        self.variables = []
        self.alphabet = {}
        self.markov_process = MarkovProcess(order)
        self._dac_achieved = False
        self._logger = logging.getLogger(__name__)
        self._init_variables(variables)

    def _init_variables(self, variables):
        for i, values in enumerate(variables):
            domain = []
            for v in values:
                value = self.get_value(v)
                value.domains[i] = True
                domain.append(value)
            self.variables.append(domain)

    def get_value(self, v):
        return self.alphabet.setdefault(v, Value(v, self.size))

    def parse(self, sequence):
        self.markov_process.parse([self.get_value(v) for v in sequence])

    def achieve_dac(self):
        """
        Achieve directional arc consistency. Exploits the chain structure to have optimal constraint propagation
        """
        dac_start = datetime.now()
        for i in reversed(xrange(self.markov_process.order, self.size)):
            self.revise(i)
        self._dac_achieved = True
        dac_time = datetime.now() - dac_start
        self._logger.info("Sequence length: {:}\t(Directed) Arc Consistency: {:}".format(self.size, dac_time))

    def revise(self, i):
        """
        Delete values from the domain of the prefixes of xi to obtain arc-consistency
        :param i: the variable index
        :return:
        """
        for y in self.variables[i]:
            for prefix in self.markov_process.transposed[y]:
                if accept(prefix, i):
                    current = y
                    for k, v in enumerate(reversed(prefix)):
                        v.link(current, i - k - 1)
                        current = v

        # filter domains by excluding non linked values
        for k in xrange(self.markov_process.order - 1):
            j = i - k - 1
            self.variables[j] = [v for v in self.variables[j] if v.ins[j] and v.outs[j]]

        # the case of the small index is special (it does not have incoming links yet)
        j = i - self.markov_process.order
        self.variables[j] = [v for v in self.variables[j] if v.outs[j]]

    def __repr__(self):
        links = []
        for i, variable in enumerate(self.variables):
            di = []
            for value in variable:
                if value.outs[i].keys():
                    di.append('{:}->{:}'.format(value, value.outs[i].keys()))
                else:
                    di.append(str(value))
            links.append(str(i) + ' ' + str(di))
        return '\n'.join(links)

    def get_sequence(self):
        if not self._dac_achieved:
            self.achieve_dac()
        sequence = []
        for variable in self.variables:
            prefix = tuple(sequence[-self.markov_process.order:])
            item = self.markov_process.generate_item(prefix, variable)
            sequence.append(item)

        return sequence


if __name__ == '__main__':

    d = ['a', 'b', 'c']
    vs = [d for l in xrange(4)]
    vs.append(['a'])
    csp = ConstraintChain(vs, 2)
    corpus = ['bab', 'aba', 'cba', 'abc']
    for seq in corpus:
        csp.parse(seq)
    for i in xrange(10):
        print csp.get_sequence()
