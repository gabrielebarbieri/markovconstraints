import unittest
from markovchain import markov_chain
from markovchain.suffix_tree import get_suffix_tree


class TestMarkovChain(unittest.TestCase):

    constraints = [['C'], None, None, ['D']]
    corpus = ['ECDECC', 'CCEEDC']

    def test_node(self):

        n = 2
        ms = markov_chain.parse_sequences(self.corpus, max_order=n)
        mc = markov_chain.get_markov_process(ms, self.constraints)
        for _ in range(10):
            assert markov_chain.generate(mc) == ['C', 'E', 'E', 'D']


class TestSuffixTree(unittest.TestCase):

    def test_tree(self):
        tree = get_suffix_tree(['banana'])
        assert tree.get_order('nane') == 3
        tree.parse('anane')
        assert tree.get_order('nane') == 4
        assert tree.get_order('banana') == 6
        assert tree.get_order('banane') == 5
        assert tree.get_all_orders('banane') == [5, 5, 4, 3, 2, 1]
        assert tree.get_max_order('banane') == 5
        assert tree.get_max_order('banana') == 6


if __name__ == '__main__':
    unittest.main()
