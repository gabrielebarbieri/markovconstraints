__author__ = 'Gabriele'

import unittest
from markovchain.markov import MarkovNode, MarkovTree
from markovchain.csp import ConstraintChain, InconsistentArcException


class TestMarkovNode(unittest.TestCase):

    def test_node(self):
        m = MarkovNode('hello')
        m.add_continuation(MarkovNode('world'))
        m.add_continuation(MarkovNode('world'))
        m.add_continuation(MarkovNode('everybody'))
        assert m.value == 'hello'
        assert str(m) == "hello -> {'everybody': 1, 'world': 2}"

    def test_get_son(self):
        m = MarkovNode('world')
        son = m.get_son('hello')
        son2 = m.get_son('hello')
        assert son.value == 'hello'
        assert son == son2

    def test_display(self):
        m = MarkovNode('C')
        m.get_son('A')
        m.get_son('B').get_son('A')
        display = 'C -> {}\n  AC -> {}\n  BC -> {}\n    ABC -> {}\n'
        assert m.recursive_rep() == display

    def test_draw_continuation(self):
        m = MarkovNode('hello')
        for i in xrange(10):
            m.add_continuation(MarkovNode('boys'))
        for i in xrange(6):
            m.add_continuation(MarkovNode('world'))
        for i in xrange(3):
            m.add_continuation(MarkovNode('everybody'))
        m.add_continuation(MarkovNode('girls'))
        allowed = ['world', 'everybody', 'girls']
        counts = {'world': 0, 'everybody': 0, 'girls': 0, 'boys': 0}
        for i in xrange(1000):
            v = m.generate_item(allowed)
            counts[v] += 1
        assert counts['world'] > counts['everybody']
        assert counts['everybody'] > counts['girls']
        assert counts['boys'] == 0


class TestMarkovTree(unittest.TestCase):

    def test_get_node(self):
        mt = MarkovTree()
        n1 = mt.get_node('hello')
        n2 = mt.get_node('hello')
        n3 = mt.get_node('hi')
        assert n1 is n2
        assert n1 is not n3
        n1.add_continuation(MarkovNode('world'))
        assert str(n1) == "hello -> {'world': 1}"
        assert str(n2) == "hello -> {'world': 1}"
        assert str(n3) == "hi -> {}"

    def test_parse(self):
        t = MarkovTree(2)
        t.parse('missisipix')
        t.parse("pice")
        s = '''c -> {'e': 1}
  ic -> {'e': 1}
e -> {}
  ce -> {}
i -> {'p': 1, 's': 2, 'c': 1, 'x': 1}
  pi -> {'x': 1, 'c': 1}
  si -> {'p': 1, 's': 1}
  mi -> {'s': 1}
m -> {'i': 1}
p -> {'i': 2}
  ip -> {'i': 1}
s -> {'i': 2, 's': 1}
  is -> {'i': 1, 's': 1}
  ss -> {'i': 1}
x -> {}
  ix -> {}
'''
        assert str(t) == s


class TestCSP(unittest.TestCase):

    def test_csp_achieve_dac(self):
        mt = MarkovTree(1)
        s = 'missisipix'
        mt.parse(s)
        variables = [['m', 'i', 's', 'p', 'x'], ['m', 'i', 's', 'p', 'x'], ['m', 'i', 's', 'p', 'x'], ['x']]

        c = ConstraintChain(variables, mt)
        c.achieve_dac()
        assert c.get_variables() == [['i', 's'], ['m', 's', 'p'], ['i'], ['x']]
        for i in xrange(10):
            seq = c.get_sequence()
            assert len(seq) == 4
            assert seq[2] == 'i'
            assert seq[3] == 'x'

    def test_inconsistent_problem(self):
        mt = MarkovTree(1)
        s = 'missisipix'
        mt.parse(s)
        v = [['m', 'i', 's', 'p', 'x'], ['m', 'i', 's', 'p', 'x'], ['m', 'i', 's', 'p', 'x'], ['m']]
        c = ConstraintChain(v, mt)
        with self.assertRaises(InconsistentArcException) as exc_info:
            c.achieve_dac()

        assert "['m', 'i', 's', 'p', 'x']->['m']" == str(exc_info.exception)

if __name__ == '__main__':
    unittest.main()