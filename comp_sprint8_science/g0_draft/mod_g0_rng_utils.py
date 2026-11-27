def g0_rng_new(seed):
    return [(int(seed) * 2654435761 + 1013904223) & 0x7FFFFFFF]

def g0_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    if m <= 0:
        return 0
    return (st[0] >> 7) % m

def g0_shuffle(st, xs):
    k = len(xs) - 1
    while k > 0:
        st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
        r = (st[0] >> 7) % (k + 1)
        t = xs[k]
        xs[k] = xs[r]
        xs[r] = t
        k -= 1
    return xs

def g0_safe(api, floor):
    return api["rem_budget"]() > floor
