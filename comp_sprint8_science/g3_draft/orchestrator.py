def solve(api, lib, budget):
    floor = 60000
    st = [(int(api["seed"]) * 2654435761 + 4242) & 0x7FFFFFFF]
    memo = {}
    best = api["reduce_parities"](api["init_parities"])
    api["submit_best"](best, "g3_init")
    best = lib.g3_descent(api, best, st, floor, 60, 20, 400, memo)
    api["submit_best"](best, "g3_descent")
    cur = best
    stall = 0
    w = [4, 4, 4]
    while api["rem_budget"]() > floor:
        fb = lib.g3_flat_best(api, cur, st, 40, [4, 4, 5], 12, floor)
        Q = None
        op = -1
        if fb[0] is not None and fb[1] > 0:
            Q = lib.g3_flat_apply(api, cur, fb[0])
        else:
            tot = w[0] + w[1] + w[2]
            r = lib.g3_rand(st, tot)
            op = 0 if r < w[0] else (1 if r < w[0] + w[1] else 2)
            if op == 0:
                if fb[0] is not None and fb[1] >= -4:
                    Q = lib.g3_flat_apply(api, cur, fb[0])
            elif op == 1:
                Q = lib.g3_null_kick(api, cur, st, 16, 0)
            else:
                Q = lib.g3_null_kick(api, cur, st, 16, -2)
            if Q is None:
                stall += 1
                continue
        Q = lib.g3_descent(api, Q, st, floor, 10, 16, 120, memo)
        if len(Q) < len(best):
            best = Q
            cur = Q
            stall = 0
            api["submit_best"](best, "g3_escape")
            if op >= 0:
                w[op] += 3
        elif len(Q) <= len(cur) + (1 if stall > 4 else 0):
            cur = Q
            stall += 1
        else:
            stall += 1
        if stall > 14:
            cur = best
            stall = 0
    api["submit_best"](best, "g3_final")
    return best
