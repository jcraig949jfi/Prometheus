def g2_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    if m <= 0:
        return 0
    return (st[0] >> 7) % m

def g2_red(x, basis):
    for b in basis:
        t = x ^ b
        if t < x:
            x = t
    return x

def g2_echelon(vs):
    basis = []
    for v in vs:
        x = g2_red(v, basis)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return basis

def g2_span(basis):
    sp = [0]
    for b in basis:
        sp = sp + [s ^ b for s in sp]
    return sp

def g2_symdiff(P, S):
    Sset = set(S)
    Pset = set(P)
    out = [p for p in P if p not in Sset]
    for s in S:
        if s and s not in Pset:
            out.append(s)
    return out

def g2_flat_eval(P, basis3):
    cnt = {}
    for p in P:
        r = g2_red(p, basis3)
        cnt[r] = cnt.get(r, 0) + 1
    h0 = cnt.get(0, 0)
    r1 = -1
    c1 = 0
    r2 = -1
    c2 = 0
    for r, c in cnt.items():
        if r == 0:
            continue
        if c > c1:
            r2 = r1
            c2 = c1
            r1 = r
            c1 = c
        elif c > c2:
            r2 = r
            c2 = c
    best = (-99, 0, 0, 0)
    if r1 >= 0:
        best = (2 * (h0 + c1) - 15, 1, r1, 0)
    if r2 >= 0:
        g = 2 * (c1 + c2) - 16
        if g > best[0]:
            best = (g, 2, r1, r2)
    return best

def g2_flat_build(basis3, kind, r1, r2):
    sp = g2_span(basis3)
    if kind == 1:
        return [s for s in sp if s] + [s ^ r1 for s in sp]
    return [s ^ r1 for s in sp] + [s ^ r2 for s in sp]

def g2_flat_sample(P, st, mode):
    m = len(P)
    if mode == 0:
        vs = [P[g2_rand(st, m)], P[g2_rand(st, m)], P[g2_rand(st, m)]]
    else:
        a = P[g2_rand(st, m)]
        vs = [a ^ P[g2_rand(st, m)], a ^ P[g2_rand(st, m)], a ^ P[g2_rand(st, m)]]
    return g2_echelon(vs)

def g2_flat_scan(api, P, st, tries, floor, min_gain):
    m = len(P)
    if m < 6:
        return None, -99
    bg = -99
    bb = None
    bk = None
    for t in range(tries):
        if api["rem_budget"]() <= floor:
            break
        basis = g2_flat_sample(P, st, t & 1)
        if len(basis) != 3:
            continue
        ev = g2_flat_eval(P, basis)
        if ev[0] > bg:
            bg = ev[0]
            bb = basis
            bk = ev
    if bb is None or bg < min_gain:
        return None, bg
    S = g2_flat_build(bb, bk[1], bk[2], bk[3])
    return api["reduce_parities"](g2_symdiff(P, S)), bg

def g2_ranked(P, limit):
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

def g2_pair_mask(P, z):
    pos = set(P)
    U = 0
    for i in range(len(P)):
        a = P[i]
        if a == z or (a ^ z) in pos:
            U |= 1 << i
    return U

def g2_null_use(api, P, z, max_basis):
    nl = api["nullspace_gf2"](api["chi_z_cols"](P, z))
    if not nl:
        return []
    U = g2_pair_mask(P, z)
    use = [b for b in nl if b & U]
    if len(use) > max_basis:
        use = use[:max_basis]
    return use

def g2_best_y(api, P, z, use, rounds):
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

def g2_sig(P):
    s = 0
    x = 0
    for p in P:
        s = (s + p * p * 2654435761 + p * 40503) & 0xFFFFFFFFFFFF
        x = x ^ ((p * 0x9E3779B1) & 0xFFFFFFFF)
    return (len(P), s, x)

def g2_descent(api, P, floor, max_fail, max_basis, cand_limit, memo):
    P = api["reduce_parities"](P)
    while api["rem_budget"]() > floor and len(P) > 2:
        sig = g2_sig(P)
        ranked = g2_ranked(P, cand_limit)
        moved = False
        fails = 0
        for zm in ranked:
            if api["rem_budget"]() <= floor or fails >= max_fail:
                break
            z = zm[0]
            if z == 0:
                continue
            key = (sig, z)
            if key in memo:
                continue
            use = g2_null_use(api, P, z, max_basis)
            if use:
                yg = g2_best_y(api, P, z, use, 2)
                if yg[1] > 0:
                    P = api["apply_shift"](P, yg[0], z)
                    moved = True
                    break
            memo[key] = 1
            fails += 1
        if not moved:
            fr = g2_flat_scan(api, P, [len(P) * 7 + 13], 24, floor, 1)
            if fr[0] is not None and len(fr[0]) < len(P):
                P = fr[0]
                continue
            break
    return P

def g2_plateau_kick(api, P, st, max_basis, min_gain):
    m = len(P)
    if m < 3:
        return None
    for t in range(4):
        i = g2_rand(st, m)
        j = g2_rand(st, m)
        z = P[i] if i == j else P[i] ^ P[j]
        if z == 0:
            continue
        nl = api["nullspace_gf2"](api["chi_z_cols"](P, z))
        if not nl:
            continue
        k = min(len(nl), max_basis)
        y = 0
        for q in range(1 + g2_rand(st, 2)):
            y ^= nl[g2_rand(st, k)]
        if y == 0:
            continue
        Q = api["apply_shift"](P, y, z)
        if m - len(Q) >= min_gain:
            return Q
    return None

def g2_escape(api, P0, floor):
    st = [(int(api["seed"]) * 2654435761 + 97) & 0x7FFFFFFF]
    memo = {}
    best = api["reduce_parities"](P0)
    api["submit_best"](best, "g2_init")
    best = g2_descent(api, best, floor, 60, 20, 400, memo)
    api["submit_best"](best, "g2_descent")
    cur = best
    stall = 0
    while api["rem_budget"]() > floor:
        fr = g2_flat_scan(api, cur, st, 40, floor, 1)
        Q = fr[0]
        if Q is None:
            mode = g2_rand(st, 10)
            if mode < 4:
                Q = g2_flat_scan(api, cur, st, 30, floor, -3 if mode < 2 else -1)[0]
            if Q is None:
                Q = g2_plateau_kick(api, cur, st, 16, 0 if mode < 7 else -2)
            if Q is None:
                stall += 1
                continue
        Q = g2_descent(api, Q, floor, 10, 16, 120, memo)
        if len(Q) < len(best):
            best = Q
            cur = Q
            stall = 0
            api["submit_best"](best, "g2_escape")
        elif len(Q) <= len(cur) + (1 if stall > 4 else 0):
            cur = Q
            stall += 1
        else:
            stall += 1
        if stall > 14:
            cur = best
            stall = 0
    return best
