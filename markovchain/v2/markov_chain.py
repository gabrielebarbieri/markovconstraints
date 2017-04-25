def filter_values(matrix, values):
    """
    Filter a transition matrix, removing all the transitions towards suffixes that are not in the given list of values
    If values is None, do nothing
    :param matrix: the matrix to filter
    :param values: the list of suffix values to keep.
    :return: the filtered matrix
    """
    if values is None:
        return matrix
    res = {}
    for prefix, probabilities in matrix.items():
        filtered = {suffix: probabilities[suffix] for suffix in probabilities if suffix in values}
        if filtered:
            res[prefix] = filtered
    return res


def get_alphas(matrix):
    """
    Get the matrix alpha coefficients, i.e. the coefficient needed to normalize the matrix and make it ergodic
    :param matrix: the matrix where the alphas are computed
    :return: the normalization coefficients alphas
    """
    return {prefix: sum(probabilities.values()) for prefix, probabilities in matrix.items()}


def normalize(matrix, alphas):
    """
    Normalize a transition matrix, by multiplying each row by its normalization coefficient alpha
    :param matrix: the matrix to normalize
    :param alphas: the normalization coefficients.
    :return: the normalized matrix
    """
    return {prefix: {suffix: value / alphas[prefix] for suffix, value in probabilities.items()}
            for prefix, probabilities in matrix.items()}


def propagate_alphas(matrix, alphas):
    """
    Back propagate the alpha normalization coefficients to a transition matrix. If the alphas is None, do not modify
     the input matrix
    :param matrix: the matrix to where back propagate the alphas
    :param alphas: the normalization coefficients to back propagate
    :return: the modified matrix
    """
    if alphas is None:
        return matrix
    return {prefix: {suffix: value * alphas[suffix] for suffix, value in probabilities.items() if suffix in alphas}
            for prefix, probabilities in matrix.items()}


def get_constrained_process(matrix, priors, constraints):
    """
    Compute a constrained markov process that has the same distribution that the process defined by the given
     transition matrix and prior probabilities and that satisfy the given unary constraints
    :param matrix: The transition matrix describing the original markov process
    :param priors: The prior probabilities
    :param constraints: The list of unary constraints. If an element in this list is None, implies no constraint to
     apply
    :return: the constrained markov process
    """
    alphas = None
    process = []
    for values in reversed(constraints[1:]):
        filtered = filter_values(matrix, values)
        filtered = propagate_alphas(filtered, alphas)
        alphas = get_alphas(filtered)
        process.append(normalize(filtered, alphas))

    f = {k: v * alphas[k] for k, v in priors.items() if k in alphas}
    alpha = sum(f.values())
    process.append({k: v / alpha for (k, v) in f.items()})
    return list(reversed(process))

if __name__ == '__main__':
    from pprint import pprint
    M = {
        'C': {'C': 0.5, 'D': 0.25, 'E': 0.25},
        'D': {'C': 0.5, 'E': 0.5},
        'E': {'C': 0.5, 'D': 0.25, 'E': 0.25}
    }
    p = {'C': 0.5, 'D': 1.0/6, 'E': 1.0/3}
    c = [None, None, None, ['D']]

    cp = get_constrained_process(M, p, c)

    print 39.0/77, 12.0/77, 26.0/77
    for e in cp:
        print
        pprint(e)
