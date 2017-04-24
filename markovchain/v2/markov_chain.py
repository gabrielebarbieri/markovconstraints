def filter_values(matrix, values):
    if values is None:
        return matrix

    out = {}
    for k, d in matrix.items():
        f = {k: d[k] for k in values if k in d}
        if f:
            out[k] = f
    return out


def get_alphas(matrix):
    return {k: sum(d.values())for (k, d) in matrix.items()}


def normalize(matrix, alphas):
    return {k: {k1: v / alphas[k] for (k1, v) in d.items()}
            for (k, d) in matrix.items()}


def propagate_alphas(matrix, alphas):
    if alphas is None:
        return matrix
    out = {}
    for k, d in matrix.items():
        out[k] = {k1: v * alphas[k1] for (k1, v) in d.items() if k1 in alphas}
    return out


def get_constrained_process(matrix, priors, constraints):
    alphas = None
    process = []
    for values in reversed(constraints[1:]):
        F = filter_values(matrix, values)
        F = propagate_alphas(F, alphas)
        alphas = get_alphas(F)
        Z = normalize(F, alphas)
        process.append(Z)

    f = {k: v*alphas[k] for (k, v) in priors.items() if k in alphas}
    alpha = sum(f.values())
    z = {k: v / alpha for (k, v) in f.items()}
    process.append(z)
    return list(reversed(process))


M = {
    'C': {'C': 0.5, 'D': 0.25, 'E': 0.25},
    'D': {'C': 0.5, 'E': 0.5},
    'E': {'C': 0.5, 'D': 0.25, 'E': 0.25}
}
p = {'C': 0.5, 'D': 1.0/6, 'E': 1.0/3}
c = [None, None, None, ['D']]


cp = get_constrained_process(M, p, c)
for e in cp:
    print e

z = cp[0]
print sum(z.values())
print z
print 39.0/77, 12.0/77, 26.0/77