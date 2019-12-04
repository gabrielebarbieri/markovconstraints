class SuffixNode(object):

    def __init__(self, value=None):
        self.value = value
        self.sons = {}

    def create_son(self, value):
        try:
            return self.sons[value]
        except KeyError:
            son = SuffixNode(value)
            self.sons[value] = son
            return son

    def parse_sub_sequence(self, sequence):
        node = self
        for element in sequence:
            node = node.create_son(element)

    def parse(self, sequence):
        for i, _ in enumerate(sequence):
            self.parse_sub_sequence(sequence[i:])

    def get_order(self, sequence):
        if not sequence:
            return 0
        node = self
        i = 0
        for i, e in enumerate(sequence):
            try:
                node = node.sons[e]
            except KeyError:
                return i
        return i + 1

    def get_all_orders(self, sequence):
        return [self.get_order(sequence[i:]) for i, _ in enumerate(sequence)]

    def get_max_order(self, sequence):
        return max(self.get_all_orders(sequence))


def get_suffix_tree(sequences):
    tree = SuffixNode()
    for seq in sequences:
        tree.parse(seq)
    return tree
