def g0_plateau_walk(api, P, st, steps, floor, max_basis):
    m = len(P)
    cur = P
    for s in range(steps):
        if api["rem_budget"]() <= floor:
            break
        Q = lib.g0_random_kick(api, cur, st, lib.g0_rand, max_basis, -2)
        if Q is not None:
            cur = Q
    return cur

def g0_full_search(api, P0, floor, frac_target):
    st = lib.g0_rng_new(api["seed"])
    best = api["reduce_parities"](P0)
    api["submit_best"](best, "g0_init")
    best = lib.g0_descent(api, best, floor, 150, 24, 600)
    api["submit_best"](best, "g0_descent")
    cur = best
    stall = 0
    it = 0
    while api["rem_budget"]() > floor:
        it += 1
        kicks = 1 + lib.g0_rand(st, 3)
        if stall > 6:
            kicks += 1
        start = cur if lib.g0_rand(st, 4) != 0 else best
        Q = lib.g0_plateau_walk(api, start, st, kicks, floor, 24)
        if api["rem_budget"]() <= floor:
            break
        Q = lib.g0_descent(api, Q, floor, 12, 16, 120)
        if len(Q) < len(best):
            best = Q
            cur = Q
            stall = 0
            api["submit_best"](best, "g0_ls")
        elif len(Q) <= len(cur):
            cur = Q
            stall += 1
        else:
            stall += 1
            if stall > 10:
                cur = best
                stall = 0
    return best
