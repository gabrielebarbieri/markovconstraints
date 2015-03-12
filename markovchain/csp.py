from datetime import datetime
import random
import logging
import sys

__author__ = 'Gabriele'


class InconsistentArcException(Exception):
    """
    Exception thrown by the dac algorithm if the generation space is empty, i.e. the generator is not able to generate
    a new sequence.
    """
    pass


class ConstraintChain():
    """
    A Constraint Chain: two adjacent variables are constrained by a Markov Constrain.
    """

    def __init__(self, variables, model):
        # Convert values to nodes and fill the csp variables
        self._node_variables = [[model.get_node(value) for value in variable] for variable in variables]
        self.graph = model
        self._dac_achieved = False
        self._tag = 0
        self._logger = logging.getLogger(__name__)

    def achieve_dac(self):
        """
        Achieve directional arc consistency. Exploits the chain structure to have optimal constraint propagation
        """
        dac_start = datetime.now()
        l = len(self._node_variables)
        for i in xrange(l - 1, 0, -1):
            self.revise(i)
        self._dac_achieved = True
        self._logger.info("Sequence length: {:}\t(Directed) Arc Consistency: {:}".format(l, datetime.now() - dac_start))

    def revise(self, i):
        """
        Delete values from the domain of xj until the directed arc (xj,xi) is arc-consistent on the direction j->i
        """

        xj = self._node_variables[i-1]
        xi = self._node_variables[i]
        self._tag += 1

        for y in xi:
            y.tag = self._tag

        filtered = []
        for x in xj:
            add = False
            for y in x.continuations:
                if y.tag == self._tag:
                    add = True
                    break
            if add:
                filtered.append(x)

        if not filtered:
            vj = [n.value for n in xj]
            vi = [n.value for n in xi]
            raise InconsistentArcException("{:}->{:}".format(vj, vi))

        self._node_variables[i-1] = filtered

    def get_sequence(self):
        """
        Generate a constrained sequence
        """
        return self.get_sequence_and_order()[0]

    def get_sequence_and_order(self):
        """
        Generate a constrained sequence and the maximum markov orders
        """
        if not self._dac_achieved:
            self.achieve_dac()
        output = []
        orders = []
        for var in self._node_variables:
            item, order = self.get_item(output, var)
            output.append(item)
            orders.append(order)
        self._logger.debug('markov max orders: ' + str(orders))
        return output, orders

    def get_item(self, prefix, var):
        """
        Generate an item from the input variable according to the prefix
        """
        order = 0
        if not prefix:
            return random.choice(var).value, order
        order += 1
        n = self.graph.get_node(prefix[-1])
        intersection = self.get_allowed_continuation(n, var)
        for v in reversed(prefix[:-1]):
            try:
                son = n.sons[v]
                new_intersection = self.get_allowed_continuation(son, var)
                if not new_intersection:
                    break
                order += 1
                n = son
                intersection = new_intersection
            except KeyError:
                break
        return n.generate_item(intersection), order

    def get_allowed_continuation(self, node, var):
        """
        Get the intersection between the node continuations and the values in var
        """
        self._tag += 1
        for v in var:
            v.tag = self._tag

        return [n.value for n in node.continuations if n.tag == self._tag]

    def get_variables(self):
        """
        Get the values of the csp variables
        """
        return [[n.value for n in node_var] for node_var in self._node_variables]

if __name__ == '__main__':

    from markov import MarkovTree
    FORMAT = '[%(levelname).1s] %(asctime)s.%(msecs)d %(name)s: %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=FORMAT, stream=sys.stdout, datefmt=DATE_FORMAT)

    mt = MarkovTree(2)
    s = 'missisipix'
    mt.parse(s)
    domain = ['m', 'i', 's', 'p', 'x']
    vs = [domain for k in xrange(14)]
    vs.append(['s'])
    c = ConstraintChain(vs, mt)
    c.achieve_dac()
    seqs = [c.get_sequence_and_order() for k in xrange(10)]
    for seq, ords in seqs:
        print '  '.join(str(o) for o in ords)
        print '  '.join(seq)
        print
    print mt