__author__ = 'gabrielebarbieri'
import logging
from datetime import datetime
import weakref


class Value(object):

    _alphabet = weakref.WeakValueDictionary()

    def __new__(cls, value):
        obj = Value._alphabet.get(value, None)
        if not obj:
            obj = object.__new__(cls)
            Value._alphabet[value] = obj
            obj.value = value
            obj.domains = None
            obj.flags = None
        return obj

    def __repr__(self):
        return repr(self.value)


class ConstraintChain():
    """
    A Constraint Chain: two adjacent variables are constrained by a Markov Constrain.
    """

    def __init__(self, variables, model):
        self.variables = []
        self._init_variables(variables)
        self.model = model
        self._dac_achieved = False
        self._logger = logging.getLogger(__name__)

    def _init_variables(self, variables):
        l = len(variables)
        for i, values in enumerate(variables):
            domain = []
            for item in values:
                value = Value(item)
                if not value.domains:
                    value.domains = [False] * l
                    value.flags = [-1] * l
                value.domains[i] = True
                domain.append(value)
            self.variables.append(domain)

    def achieve_dac(self):
        """
        Achieve directional arc consistency. Exploits the chain structure to have optimal constraint propagation
        """
        dac_start = datetime.now()
        l = len(self.variables)
        for i in reversed(xrange(self.model.order, l)):
            self.revise(i)
        self._dac_achieved = True
        self._logger.info("Sequence length: {:}\t(Directed) Arc Consistency: {:}".format(l, datetime.now() - dac_start))

    def revise(self, i):
        """
        Delete values from the domain of the prefixes of xi to obtain arc-consistency
        :param i: the variable index
        :return:
        """
        for y in self.variables[i]:
            edges = self.model.transposed[y]
            for prefix in edges.keys():
                print i, y,
                accept = True
                for j, v in enumerate(reversed(prefix)):
                    pos = i - j - 1
                    if not v.domains[pos]:
                        accept = False
                        break
                if accept:
                    for j, v in enumerate(reversed(prefix)):
                        pos = i - j - 1
                        v.flags[pos] = i
                        print pos, v,
                print

        for k in xrange(self.model.order):
            j = i - k - 1
            if j >= 0:
                filtered = [v for v in self.variables[j] if v.flags[j] is i]
                self.variables[j] = filtered

        print

if __name__ == '__main__':
    from markov import MarkovProcess
    # from sys import stdout
    # logging.basicConfig(level=logging.INFO, stream=stdout)
    seq = 'mississipix'
    mt = MarkovProcess(2)
    mt.parse([Value(e) for e in seq])
    d = ['m', 'i', 's', 'p', 'x']
    vs = [d for ii in xrange(4)]
    vs.append(['s'])
    vs.append(['s'])
    csp = ConstraintChain(vs, mt)
    csp.achieve_dac()
    for var in csp.variables:
        print var
