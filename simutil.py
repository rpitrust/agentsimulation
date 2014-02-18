
def meanstd(x):
    from math import sqrt
    n, mean, std = len(x), 0, 0
    if n == 0:
        return 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    if n == 1:
        return mean, 0
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std
