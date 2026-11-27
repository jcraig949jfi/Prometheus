def g0_pair_counts(P):
    counts = {}
    m = len(P)
    for i in range(m):
        a = P[i]
        counts[a] = counts.get(a, 0) + 1
        for j in range(i + 1, m):
            z = a ^ P[j]
            counts[z] = counts.get(z, 0) + 1
    return counts

def g0_ranked_shifts(P, limit):
    counts = g0_pair_counts(P)
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit > 0 and len(items) > limit:
        items = items[:limit]
    return items

def g0_null_for(api, P, z):
    cols = api["chi_z_cols"](P, z)
    if not cols:
        return []
    return api["nullspace_gf2"](cols)

def g0_pair_mask(P, z):
    pos = {}
    for i in range(len(P)):
        pos[P[i]] = i
    U = 0
    for i in range(len(P)):
        a = P[i]
        if a == z or (a ^ z) in pos:
            U |= 1 << i
    return U

def g0_best_in_null(api, P, z, nl, max_basis, accept_gain):
    m = len(P)
    if not nl:
        return None, -999
    U = g0_pair_mask(P, z)
    use = []
    for b in nl:
        if b & U:
            use.append(b)
    if not use:
        return None, -999
    if len(use) > max_basis:
        use = use[:max_basis]
    best_y = 0
    best_len = m + 2
    for b in use:
        L = len(api["apply_shift"](P, b, z))
        if L < best_len:
            best_len = L
            best_y = b
    improved = True
    rounds = 0
    while improved and rounds < 2:
        improved = False
        rounds += 1
        for b in use:
            y2 = best_y ^ b
            if y2 == 0:
                continue
            L = len(api["apply_shift"](P, y2, z))
            if L < best_len:
                best_len = L
                best_y = y2
                improved = True
    gain = m - best_len
    if gain < accept_gain:
        return None, gain
    return api["apply_shift"](P, best_y, z), gain

def g0_try_shift(api, P, z, max_basis, accept_gain):
    nl = g0_null_for(api, P, z)
    return g0_best_in_null(api, P, z, nl, max_basis, accept_gain)

def g0_descent(api, P, floor, max_fail, max_basis, cand_limit):
    P = api["reduce_parities"](P)
    while api["rem_budget"]() > floor and len(P) > 1:
        ranked = g0_ranked_shifts(P, cand_limit)
        moved = False
        fails = 0
        for zm in ranked:
            if api["rem_budget"]() <= floor:
                break
            z = zm[0]
            if z == 0:
                continue
            if 2 * zm[1] + 2 < 2:
                break
            Q, g = g0_try_shift(api, P, z, max_basis, 1)
            if Q is not None and len(Q) < len(P):
                P = Q
                moved = True
                break
            fails += 1
            if fails >= max_fail:
                break
        if not moved:
            break
    return P

def g0_random_kick(api, P, st, rand_fn, max_basis, min_gain):
    m = len(P)
    if m < 2:
        return None
    i = rand_fn(st, m)
    j = rand_fn(st, m)
    if i == j:
        z = P[i]
    else:
        z = P[i] ^ P[j]
    if z == 0:
        return None
    nl = g0_null_for(api, P, z)
    if not nl:
        return None
    y = 0
    k = len(nl)
    if k > max_basis:
        k = max_basis
    picks = 1 + rand_fn(st, 3)
    for t in range(picks):
        y ^= nl[rand_fn(st, k)]
    if y == 0:
        y = nl[0]
    Q = api["apply_shift"](P, y, z)
    if m - len(Q) < min_gain:
        return None
    return Q
