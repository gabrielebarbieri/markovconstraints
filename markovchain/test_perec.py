import json
import os
from datetime import datetime

from markovchain import markov_chain
from suffix_tree import get_suffix_tree


def parse_tags(root):
    sentences = []
    for file_name in os.listdir(root):
        with open(os.path.join(root, file_name)) as f_in:
            for line in f_in.readlines():
                if line.strip():
                    data = json.loads(line)
                    sentences.append([tag['word'] for tag in data['tags']])
    return sentences

t = datetime.now()
corpus = parse_tags('/Users/gabriele/Workspace/misc/perec/perec OLD/corpus/Dylan')
print 'time to load the corpus', datetime.now() - t

t = datetime.now()
ms = markov_chain.parse_sequences(corpus, 3)
print 'time to estimate the matrices', datetime.now() - t

t = datetime.now()
mp = markov_chain.get_markov_process(ms, ['i'] + [None] * 10 + ['.'])
print 'time to compute the markov process', datetime.now() - t

t = datetime.now()
tree = get_suffix_tree(corpus)
print 'time to compute the suffix tree', datetime.now() - t

t = datetime.now()
for i in xrange(10):
    seq = markov_chain.generate(mp)
    print ' '.join(seq) + ' (ord:{})'.format(tree.get_max_order(seq))
print datetime.now() - t
