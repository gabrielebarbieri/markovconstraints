import numpy as np


def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
    return c


def get_alphas(A):
    return np.squeeze(np.asarray(A.sum(axis=1)))


def normalize(alphas, A):
    return np.diag(div0(1, alphas)) * A

M = np.matrix([
    [0.5, 0.25, 0.25],
    [0.5, 0, 0.5],
    [0.5, 0.25, 0.25]
])
p = np.array([0.5, 1.0/6, 1.0/3])

n = M.shape[0]
D = {1}

I = np.diag([i if i in D else 0 for i in xrange(n)])

F = M * I
alphas = get_alphas(F)
Z = normalize(alphas, F)
print Z
print

F = M * np.diag(alphas)
alphas = get_alphas(F)
Z = normalize(alphas, F)
print Z
print

F = M * np.diag(alphas)
alphas = get_alphas(F)
Z = normalize(alphas, F)
print Z
print


f = p.dot(np.diag(alphas))
alpha = f.sum()
z = f/alpha
print z.sum()


print 39.0/77, 12.0/77, 26.0/77

