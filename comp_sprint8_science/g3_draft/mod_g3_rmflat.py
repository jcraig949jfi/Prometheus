def g3_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    if m <= 0:
        return 0
    return (st[0] >> 7) % m

def g3_flat_grow(P, Pset, st, dim, linear, width):
    m = len(P)
    if linear:
        F = [0]
        c = 0
    else:
        F = [P[g3_rand(st, m)]]
        c = 1
    Fset = set(F)
    for step in range(dim):
        bv = 0
        bc = -1
        for k in range(width):
            p = P[g3_rand(st, m)]
            if p in Fset:
                continue
            v = p ^ F[0]
            cc = 0
            for f in F:
                if (f ^ v) in Pset:
                    cc += 1
            if cc > bc:
                bc = cc
                bv = v
        if bc < 0:
            return None, -999
        F = F + [f ^ bv for f in F]
        Fset = set(F)
        c += bc
    size = len(F) - (1 if linear else 0)
    return F, 2 * c - size

def g3_flat_best(api, P, st, tries, dims, width, floor):
    m = len(P)
    if m < 8:
        return None, -999
    Pset = set(P)
    bF = None
    bg = -999
    for t in range(tries):
        if api["rem_budget"]() <= floor:
            break
        dim = dims[g3_rand(st, len(dims))]
        if (1 << dim) > 2 * m + 2:
            continue
        r = g3_flat_grow(P, Pset, st, dim, g3_rand(st, 2) == 0, width)
        if r[0] is not None and r[1] > bg:
            bg = r[1]
            bF = r[0]
    return bF, bg

def g3_flat_apply(api, P, F):
    return api["reduce_parities"](P + [f for f in F if f])

def g3_pair_ranked(P, limit):
    counts = {}
    m = len(P)
    for i in range(m):
        a = P[i]
        counts[a] = counts.get(a, 0) + 1
        for j in range(i + 1, m):
            z = a ^ P[j]
            counts[z] = counts.get(z, 0) + 1
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    if len(items) > limit:
        items = items[:limit]
    return items

def g3_sig(P):
    s = 0
    x = 0
    for p in P:
        s = (s + p * p * 2654435761 + p * 40503) & 0xFFFFFFFFFFFF
        x = x ^ ((p * 0x9E3779B1) & 0xFFFFFFFF)
    return (len(P), s, x)

def g3_null_best(api, P, z, max_basis, rounds):
    nl = api["nullspace_gf2"](api["chi_z_cols"](P, z))
    if not nl:
        return 0, -999
    pos = set(P)
    U = 0
    for i in range(len(P)):
        a = P[i]
        if a == z or (a ^ z) in pos:
            U |= 1 << i
    use = [b for b in nl if b & U]
    if not use:
        return 0, -999
    if len(use) > max_basis:
        use = use[:max_basis]
    m = len(P)
    by = 0
    bl = m + 99
    for b in use:
        L = len(api["apply_shift"](P, b, z))
        if L < bl:
            bl = L
            by = b
    r = 0
    imp = True
    while imp and r < rounds:
        imp = False
        r += 1
        for b in use:
            y2 = by ^ b
            if y2 == 0:
                continue
            L = len(api["apply_shift"](P, y2, z))
            if L < bl:
                bl = L
                by = y2
                imp = True
    return by, m - bl

def g3_descent(api, P, st, floor, max_fail, max_basis, cand_limit, memo):
    P = api["reduce_parities"](P)
    while api["rem_budget"]() > floor and len(P) > 2:
        sig = g3_sig(P)
        moved = False
        fails = 0
        for zm in g3_pair_ranked(P, cand_limit):
            if api["rem_budget"]() <= floor or fails >= max_fail:
                break
            z = zm[0]
            if z == 0:
                continue
            key = (sig, z)
            if key in memo:
                continue
            yg = g3_null_best(api, P, z, max_basis, 2)
            if yg[1] > 0:
                P = api["apply_shift"](P, yg[0], z)
                moved = True
                break
            memo[key] = 1
            fails += 1
        if not moved:
            fb = g3_flat_best(api, P, st, 24, [4, 4, 5], 10, floor)
            if fb[0] is not None and fb[1] > 0:
                P = g3_flat_apply(api, P, fb[0])
                continue
            break
    return P

def g3_null_kick(api, P, st, max_basis, min_gain):
    m = len(P)
    if m < 3:
        return None
    for t in range(4):
        i = g3_rand(st, m)
        j = g3_rand(st, m)
        z = P[i] if i == j else P[i] ^ P[j]
        if z == 0:
            continue
        nl = api["nullspace_gf2"](api["chi_z_cols"](P, z))
        if not nl:
            continue
        k = min(len(nl), max_basis)
        y = 0
        for q in range(1 + g3_rand(st, 2)):
            y ^= nl[g3_rand(st, k)]
        if y == 0:
            continue
        Q = api["apply_shift"](P, y, z)
        if m - len(Q) >= min_gain:
            return Q
    return None
